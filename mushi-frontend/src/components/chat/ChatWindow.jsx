// mushi-frontend/src/components/chat/ChatWindow.jsx
import React, { useState, useRef, useEffect, useMemo } from 'react';
import { api } from '../../services/api';
import QuestionPrompts from './QuestionPrompts';
import SpoilerText from './SpoilerText';
import { Send, Bot, User, XCircle, Edit3, Eye, EyeOff, Mic, StopCircle, Copy } from 'lucide-react';
import SpeechToText from './SpeechToText';

// llm-ui imports for streaming and markdown rendering
import { useLLMOutput, throttleBasic } from "@llm-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { markdownLookBack } from "@llm-ui/markdown";

// --- llm-ui Components and Blocks ---

// Markdown Fallback Component: Renders general markdown content
const MarkdownComponent = ({ blockMatch }) => {
  const markdown = blockMatch.output;
  return <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>;
};

// Custom Spoiler Block Component: Renders content within <spoiler> tags using SpoilerText
const SpoilerBlockComponent = ({ blockMatch }) => {
  return (
    <SpoilerText globalShieldActive={blockMatch.block.props.globalShieldActive}>
      {blockMatch.outputRaw}
    </SpoilerText>
  );
};

// Custom Spoiler Block Definition for llm-ui
const baseSpoilerBlock = {
  findCompleteMatch: (llmOutput) => {
    const match = llmOutput.match(/<spoiler>(.*?)<\/spoiler>/s);
    if (match) {
      return {
        startIndex: match.index,
        endIndex: match.index + match[0].length,
        outputRaw: match[1],
      };
    }
    return undefined;
  },
  findPartialMatch: (llmOutput) => {
    const match = llmOutput.match(/<spoiler>(.*)/s);
    if (match) {
      return {
        startIndex: match.index,
        endIndex: llmOutput.length,
        outputRaw: match[1],
      };
    }
    return undefined;
  },
  component: SpoilerBlockComponent,
  lookBack: (params) => {
    return {
      output: params.output,
      visibleText: params.output,
    };
  },
  props: { globalShieldActive: false },
};

// Updated: Custom block for generic "NOTE"s embedded in main response
const GenericNoteBlockComponent = ({ blockMatch }) => {
  const fullNoteString = blockMatch.outputRaw.trim(); // The complete string matched by the block

  // Robustly extract the note type and content from the full matched string
  const typeMatch = fullNoteString.match(/^([A-Z_]+):/);
  const noteType = typeMatch ? typeMatch[1] : 'GENERIC_NOTE';
  const contentWithoutType = typeMatch ? fullNoteString.substring(typeMatch[0].length).trim() : fullNoteString;

  // Dynamically create a user-friendly heading based on the note type
  const displayHeading = noteType.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());

  // Function to robustly format list content for ReactMarkdown
  const formatListContent = (content) => {
    // This regex looks for `- **` pattern as the start of a new list item.
    // It will prepend a newline before each occurrence of `- **` that is not at the very beginning
    // to force markdown to interpret them as new list items.
    let formatted = content.replace(/([^\n])-\s?\*\*/g, '$1\n- **');

    // Ensure the very first item also starts on its own line and with a markdown list prefix.
    // This handles cases where the LLM might output "NOTE TYPE:Item 1- Item 2"
    if (!formatted.startsWith('- ')) {
        formatted = `- ${formatted}`;
    }
    // Remove any trailing empty list items or excessive newlines at the end
    formatted = formatted.replace(/(\n- \s*)*$/, '');

    // Ensure overall content starts with a newline for proper markdown interpretation if it's a list
    return formatted.startsWith('\n') ? formatted : `\n${formatted}`;
  };

  return (
    <div className="mt-4 pt-2 border-t border-gray-600"> {/* Add some top margin and border for separation */}
      <p className="font-bold underline mb-1 text-purple-300">{displayHeading}:</p> {/* Dynamic heading */}
      {/* Prepend a newline to ensure ReactMarkdown interprets subsequent hyphens as a list */}
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{formatListContent(contentWithoutType)}</ReactMarkdown>
    </div>
  );
};

// Updated: Definition for the Generic Note Block
const baseGenericNoteBlock = {
  findCompleteMatch: (llmOutput) => {
    // Look for "NOTE TYPE:" and capture the type and everything after it
    const match = llmOutput.match(/NOTE\s+([A-Z_]+):(.*)/s);
    if (match) {
      return {
        startIndex: match.index,
        endIndex: llmOutput.length, // Consumes the rest of the output
        outputRaw: match[0], // Pass the full matched string to the component for parsing
        props: { noteType: match[1] } // Capture the note type (used for heading generation, but component is robust without it)
      };
    }
    return undefined;
  },
  findPartialMatch: (llmOutput) => {
    // Partial match if the prefix is found and content follows
    const match = llmOutput.match(/NOTE\s+([A-Z_]+):(.*)/s);
    if (match) {
      return {
        startIndex: match.index,
        endIndex: llmOutput.length,
        outputRaw: match[0], // Pass the full matched string
        props: { noteType: match[1] }
      };
    }
    return undefined;
  },
  component: GenericNoteBlockComponent,
  lookBack: (params) => ({
    output: params.output,
    visibleText: params.output,
  }),
};


function ChatWindow({ initialQuery }) {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Welcome to Mushi AI. How can I help you today?', id: 'welcome-message' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [similarAnimeNote, setSimilarAnimeNote] = useState(null);
  const [isSpoilerShieldActive, setIsSpoilerShieldActive] = useState(false);
  const [isSpeechActive, setIsSpeechActive] = useState(false);
  const [speechRecognitionError, setSpeechRecognitionError] = useState('');
  const abortControllerRef = useRef(null);

  // States for the currently streaming bot message (only for live display)
  const [currentStreamingBotMessage, setCurrentStreamingBotMessage] = useState('');
  const [isLLMStreamFinished, setIsLLMStreamFinished] = useState(false);


  // Ref for the messages container to enable auto-scrolling
  const messagesEndRef = useRef(null);
  // State for copy feedback
  const [copiedMessageId, setCopiedMessageId] = useState(null);

  // States for in-place editing
  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editingMessageText, setEditingMessageText] = useState('');
  const originalMessageTextRef = useRef(null);
  const textareaRef = useRef(null);

  // Store the last user query for suggested questions
  const lastUserQueryForSuggestions = useRef('');


  // Effect to scroll to the bottom of the chat when messages change
  // Removed currentStreamingBotMessage from dependencies to prevent excessive scrolling during streaming.
  // Scrolling will now primarily happen when a message is finalized or suggestions appear.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, suggestedQuestions, similarAnimeNote]);

  // Effect to adjust textarea height when editingMessageText changes
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [editingMessageText, editingMessageId]);

  useEffect(() => {
    if (initialQuery) {
      console.log("Mushi received a preloaded query!~", initialQuery);
      handleSendMessage(initialQuery);
    }
  }, [initialQuery]); // This effect runs only when the initialQuery prop changes


  // llm-ui Throttle function configuration - OPTIMIZED FOR EVEN SMOOTHER TYPING EFFECT
  const throttle = useMemo(() => throttleBasic({
    readAheadChars: 3,        // Increased to 3 for slightly larger chunks, reducing re-render strain
    targetBufferChars: 3,     // Keep the visible buffer consistent with readAhead
    adjustPercentage: 0.2,    // Allow for slightly larger speed adjustments
    frameLookBackMs: 10000,
    windowLookBackMs: 2000,
  }), []);

  // llm-ui Blocks configuration, including the dynamic spoilerBlock and new GenericNoteBlock
  const blocks = useMemo(() => [
    { ...baseSpoilerBlock, props: { globalShieldActive: isSpoilerShieldActive } },
    baseGenericNoteBlock, // Use the new generic note block here
  ], [isSpoilerShieldActive]);

  // useLLMOutput hook to manage the streaming display
  const { blockMatches } = useLLMOutput({
    llmOutput: currentStreamingBotMessage,
    blocks: blocks,
    fallbackBlock: {
      component: MarkdownComponent,
      lookBack: markdownLookBack(),
    },
    isStreamFinished: isLLMStreamFinished,
    throttle,
  });


  // Helper function to encapsulate the LLM interaction logic
  const processQueryAndGetResponse = async (queryToProcess) => {
    setSuggestedQuestions([]);
    setSimilarAnimeNote(null);
    setIsLoading(true); // Start overall loading indicator

    // Add user message immediately to the chat history
    const userMessageId = `user-${Date.now()}`;
    setMessages(prev => [...prev, { sender: 'user', text: queryToProcess, id: userMessageId }]);

    // Store the user's query for suggestions
    lastUserQueryForSuggestions.current = queryToProcess;

    // Reset llm-ui related states for the new stream
    setCurrentStreamingBotMessage('');
    setIsLLMStreamFinished(false);

    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    let accumulatedBotResponse = ''; // This will collect the full response for suggestions and final storage

    try {
      // Call the streaming chat API. onChunkReceived will update currentStreamingBotMessage
      await api.llm.chat(queryToProcess, (chunk) => {
        accumulatedBotResponse += chunk;
        setCurrentStreamingBotMessage(accumulatedBotResponse); // Update the state for useLLMOutput
      }, signal);

      // Stream finished successfully. accumulatedBotResponse holds final text.
      setIsLLMStreamFinished(true); // Signal to useLLMOutput that the stream is complete

    } catch (error) {
      // Stream finished due to an error or user abort
      setIsLLMStreamFinished(true); // Signal completion (even if erroneous)

      let errorMessageText = `Sorry, something went wrong: ${error.message}.`;
      if (error.name === 'AbortError') {
        errorMessageText = "Mushi stopped generating, desu!";
      } else if (error.message.includes("Error: Ollama server is not running")) {
        errorMessageText = "Mushi can't connect to Ollama server, Senpai! Please make sure it's running. (T_T)";
      } else if (error.message.includes("Ollama generation took too long")) {
        errorMessageText = "Mushi took too long to think, Senpai! Maybe the model is too big? Gomen'nasai...";
      }

      console.error('LLM chat error:', error);
      accumulatedBotResponse = errorMessageText; // Use error message as accumulated response
      setCurrentStreamingBotMessage(errorMessageText); // Display error immediately via llm-ui
    } finally {
      // Important: After llm-ui finishes rendering the stream (or error message)
      // and currentStreamingBotMessage has its final content, add it to history.
      // This sequence prevents the double display.
      if (accumulatedBotResponse) { // Only add if there's content to add (including error messages)
        setMessages(prev => [...prev, { sender: 'bot', text: accumulatedBotResponse, id: `bot-final-${Date.now()}` }]);
      }
      setCurrentStreamingBotMessage(''); // Clear the temporary streaming display content

      // Fetch suggested questions only after the main LLM response is complete and finalized in history
      if (accumulatedBotResponse && !accumulatedBotResponse.startsWith("Error:") && abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        try {
          const suggestionsResponse = await api.llm.getSuggestedQuestions(accumulatedBotResponse);
          if(suggestionsResponse) {
              setSuggestedQuestions(suggestionsResponse.suggested_questions || []);
              setSimilarAnimeNote(suggestionsResponse.similar_anime_note || null);
          }
        } catch (suggestError) {
          console.error('Error fetching suggested questions:', suggestError);
          setSimilarAnimeNote(prev => prev ? prev + "\nError fetching suggestions." : "Error fetching suggestions.");
        }
      }
      setIsLoading(false); // Overall loading finished
      abortControllerRef.current = null;
    }
  };

  // handleSendMessage now only handles new user message submission
  const handleSendMessage = async (query) => {
    if (!query || isLoading) return;

    setInputValue(''); // Clear input after sending

    // Call the new helper to handle the actual LLM interaction
    await processQueryAndGetResponse(query);
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort('User stopped generation');
      console.log('LLM generation stopped by user.');
      setIsLoading(false);
      setIsLLMStreamFinished(true); // Signal to useLLMOutput to finalize
    }
  };

  const handleEditMessage = (messageText, index) => {
    if (isLoading) {
      handleStopGeneration();
    }
    setIsSpeechActive(false);

    if (editingMessageId !== null && editingMessageId !== index) {
      handleSaveEdit(editingMessageId);
    }

    const textToEdit = Array.isArray(messageText) ?
                       messageText.map(part => typeof part === 'string' ? part : '').join('') :
                       messageText;

    setEditingMessageId(index);
    setEditingMessageText(textToEdit);
    originalMessageTextRef.current = textToEdit;
  };

  const handleSaveEdit = (index) => {
    if (editingMessageText.trim() !== originalMessageTextRef.current.trim()) {
      lastUserQueryForSuggestions.current = editingMessageText;
      processQueryAndGetResponse(editingMessageText);
    } else {
      console.log("No changes detected in edited message, not resubmitting.");
    }

    setEditingMessageId(null);
    setEditingMessageText('');
    originalMessageTextRef.current = null;
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditingMessageText('');
    originalMessageTextRef.current = null;
  };

  const handleEditKeyDown = (e, index) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSaveEdit(index);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (editingMessageId !== null && inputValue.trim() === '') {
      handleSaveEdit(editingMessageId);
    } else if (inputValue.trim()) {
      handleSendMessage(inputValue);
    }
  };

  const handleCopy = (textToCopy, messageId) => {
    const tempTextArea = document.createElement('textarea');
    tempTextArea.value = textToCopy;
    document.body.appendChild(tempTextArea);
    tempTextArea.select();
    try {
      document.execCommand('copy');
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    } finally {
      document.body.removeChild(tempTextArea);
    }
  };

  const handleSpeechToTextTranscript = (transcript) => {
    setInputValue(transcript);
  };

  const handleSpeechRecordingStatusChange = (status) => {
    setIsSpeechActive(status);
    if (!status && inputValue) {
      setSpeechRecognitionError('');
    }
  };

  const handleSpeechError = (errorMsg) => {
    setSpeechRecognitionError(errorMsg);
    setIsSpeechActive(false);
  };

  const handleMicrophoneClick = () => {
    if (isSpeechActive) {
      setIsSpeechActive(false);
    } else {
      if (isLoading) {
        handleStopGeneration();
      }
      setInputValue('');
      setSpeechRecognitionError('');
      setIsSpeechActive(true);
    }
  };

  const handleClearChat = () => {
    setMessages([{ sender: 'bot', text: 'Welcome to Mushi AI. How can I help you today?', id: 'welcome-message' }]);
    setSuggestedQuestions([]);
    setSimilarAnimeNote(null);
    setInputValue('');
    setIsLoading(false);
    setEditingMessageId(null);
    setEditingMessageText('');
    originalMessageTextRef.current = null;
    setIsSpeechActive(false);
    setSpeechRecognitionError('');
    if (abortControllerRef.current) {
      abortControllerRef.current.abort('Chat cleared by user');
    }
    lastUserQueryForSuggestions.current = '';
    setCurrentStreamingBotMessage('');
    setIsLLMStreamFinished(false);
  };


  return (
    <div className="flex flex-col h-full bg-neutral-950 p-4 rounded-lg shadow-2xl border border-white/10">
      <h2 className="text-xl font-bold mb-4 text-center
                       bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400
                       drop-shadow-lg [text-shadow:0_0_10px_rgba(255,100,255,0.2)]">
        Mushi AI Chat
      </h2>

      <div ref={messagesEndRef} className="flex-grow overflow-y-auto p-4 space-y-4 custom-scrollbar pb-4 rounded-xl bg-white/5 border border-white/10">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
            {msg.sender === 'bot' && ( // Render all completed bot messages
              <>
                <Bot className="w-6 h-6 text-purple-400 flex-shrink-0" />
                <div className={`max-w-2xl p-4 rounded-2xl bg-gray-700 text-gray-200 shadow-md`}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                </div>
                <button
                  onClick={() => handleCopy(msg.text, msg.id)}
                  className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-gray-600 flex-shrink-0"
                  title="Copy message"
                >
                  <Copy size={16} />
                </button>
                {copiedMessageId === msg.id && <span className="text-xs text-green-400 ml-1">Copied!</span>}
              </>
            )}
            {msg.sender === 'user' && (
              <>
                {editingMessageId === msg.id ? (
                  <div className={`max-w-xl p-4 rounded-2xl bg-purple-600 text-white shadow-md`}>
                    <textarea
                      ref={textareaRef}
                      className="w-full bg-purple-700 text-white p-2 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-pink-400 overflow-hidden"
                      value={editingMessageText}
                      onChange={(e) => setEditingMessageText(e.target.value)}
                      onKeyDown={(e) => handleEditKeyDown(e, msg.id)}
                      rows={1}
                    />
                  </div>
                ) : (
                  <div className={`max-w-xl p-4 rounded-2xl bg-purple-600 text-white shadow-md`}>
                    <p className="text-base leading-relaxed font-sans">
                      {msg.text}
                    </p>
                  </div>
                )}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <User className="w-6 h-6 text-pink-400" />
                  {editingMessageId === msg.id ? (
                    <>
                      <button
                        onClick={() => handleSaveEdit(msg.id)}
                        className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-gray-600"
                        title="Save changes"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucude-check"><path d="M20 6 9 17l-5-5"/></svg>
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-gray-600"
                        title="Cancel edit"
                      >
                        <XCircle size={16} />
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleEditMessage(msg.text, msg.id)}
                      className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-gray-600"
                      title="Edit message"
                    >
                      <Edit3 size={16} />
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        ))}

        {/* NEW: Render the currently streaming bot message using llm-ui. This replaces the old placeholder logic. */}
        {currentStreamingBotMessage && ( // Only show this if there's a message actively streaming
            <div key="streaming-bot-live" className="flex items-start gap-3">
                <Bot className="w-6 h-6 text-purple-400 flex-shrink-0" />
                <div className={`max-w-2xl p-4 rounded-2xl bg-gray-700 text-gray-200 shadow-md`}>
                    {/* Render llm-ui block matches */}
                    {blockMatches.map((blockMatch, idx) => {
                        const Component = blockMatch.block.component;
                        return <Component key={idx} blockMatch={blockMatch} />;
                    })}
                </div>
            </div>
        )}

        {/* Adjust isLoading indicator logic */}
        {isLoading && !currentStreamingBotMessage && <div className="text-center text-purple-400">Mushi is thinking...</div>}
      </div>

      {/* Suggested Questions */}
      <QuestionPrompts questions={suggestedQuestions} onQuestionClick={handleSendMessage} />

      {/* Similar Anime Note */}
      {similarAnimeNote && (
        <div className="px-4 py-3 border border-pink-500 rounded-lg mb-4 bg-white/5 text-pink-300 text-sm shadow-md">
          {/* Render "Similar Anime:" underlined and bold */}
          <p className="font-bold underline mb-2 text-purple-400">Similar Anime:</p>
          {/* Render the rest of the note using ReactMarkdown to handle list formatting */}
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {similarAnimeNote.startsWith("Similar anime: ")
              ? similarAnimeNote.substring("Similar anime: ".length).trim()
              : similarAnimeNote // Fallback in case format changes unexpectedly
            }
          </ReactMarkdown>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleFormSubmit} className="flex items-center gap-2 border-t border-white/10 pt-4">
        {/* Clear Chat Button */}
        <button
          type="button"
          onClick={handleClearChat}
          className="p-3 rounded-full bg-white/10 text-gray-300 hover:text-white hover:bg-pink-600 transition-colors duration-200 flex items-center justify-center shadow-md"
          title="Clear Chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-trash-2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
        </button>

        {/* Spoiler Shield Toggle Button */}
        <button
          type="button"
          onClick={() => setIsSpoilerShieldActive(prev => !prev)}
          className={`p-3 rounded-full transition-colors duration-200 flex items-center justify-center shadow-md ${
            isSpoilerShieldActive ? 'bg-purple-600 text-white' : 'bg-white/10 text-gray-300 hover:text-white hover:bg-purple-600'
          }`}
          title={isSpoilerShieldActive ? "Spoiler Shield: Active" : "Spoiler Shield: Inactive"}
        >
          {isSpoilerShieldActive ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>

        {/* Microphone Button */}
        <button
          type="button"
          onClick={handleMicrophoneClick}
          className={`p-3 rounded-full transition-colors duration-200 flex items-center justify-center shadow-md ${
            isSpeechActive ? 'bg-pink-600 text-white' : 'bg-white/10 text-gray-300 hover:text-white hover:bg-pink-600'
          }`}
          title={isSpeechActive ? "Stop recording" : "Start recording"}
          disabled={isLoading}
        >
          {isSpeechActive ? <StopCircle size={20} /> : <Mic size={20} />}
        </button>

        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={isSpeechActive ? "Listening for your voice..." : "Ask Mushi anything..."}
          className="flex-grow bg-white/10 rounded-full py-3 px-4 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-pink-500 border border-white/20 transition-all duration-300"
          disabled={isLoading || isSpeechActive || editingMessageId !== null}
        />

        {/* Conditional rendering for Stop button (when LLM is loading) or Send button */}
        {isLoading ? (
          <button
            type="button"
            onClick={handleStopGeneration}
            className="bg-pink-600 hover:bg-pink-700 text-white p-3 rounded-full transition-colors duration-200 flex items-center justify-center shadow-md"
            title="Stop generation"
          >
            <XCircle size={20} />
          </button>
        ) : (
          <button
            type="submit"
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white p-3 rounded-full transition-colors duration-200 flex items-center justify-center shadow-md"
            disabled={!inputValue.trim() && editingMessageId === null || isSpeechActive}
            title={editingMessageId !== null ? "Save Edited Question" : "Send New Question"}
          >
            {editingMessageId !== null ?
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucude-check"><path d="M20 6 9 17l-5-5"/></svg>
              : <Send size={20} />
            }
          </button>
        )}
      </form>
      {/* Recording in progress indicator */}
      {isSpeechActive && <p className="text-center text-pink-400 text-sm mt-2">Recording in progress... Speak now!</p>}
      {/* Display speech recognition errors */}
      {speechRecognitionError && <p className="text-center text-red-300 text-sm mt-2">{speechRecognitionError}</p>}


      {/* SpeechToText component: This handles the underlying speech recognition logic */}
      <SpeechToText
        onTranscript={handleSpeechToTextTranscript}
        onRecordingStatusChange={handleSpeechRecordingStatusChange}
        shouldStartRecording={isSpeechActive}
        onSpeechError={handleSpeechError}
      />
    </div>
  );
}

export default ChatWindow;
