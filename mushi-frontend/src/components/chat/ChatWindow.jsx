// mushi-frontend/src/components/chat/ChatWindow.jsx
import React, { useState, useRef, useEffect } from 'react';
import { api } from '../../services/api';
import QuestionPrompts from './QuestionPrompts';
import SpoilerText from './SpoilerText';
// Import new icons for microphone, stop circle, and Copy
import { Send, Bot, User, XCircle, Edit3, Eye, EyeOff, Mic, StopCircle, Copy } from 'lucide-react';
import SpeechToText from './SpeechToText'; // Import the new SpeechToText component
import axios from 'axios';

function ChatWindow() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Welcome to Mushi AI. How can I help you today?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [similarAnimeNote, setSimilarAnimeNote] = useState(null); // New state for similar anime note
  const [isSpoilerShieldActive, setIsSpoilerShieldActive] = useState(false);
  const [isSpeechActive, setIsSpeechActive] = useState(false);
  const [speechRecognitionError, setSpeechRecognitionError] = useState('');
  const abortControllerRef = useRef(null);

  // Ref for the messages container to enable auto-scrolling
  const messagesEndRef = useRef(null);
  // State for copy feedback
  const [copiedMessageId, setCopiedMessageId] = useState(null);

  // New states for in-place editing
  const [editingMessageId, setEditingMessageId] = useState(null); // Stores the index of the message being edited
  const [editingMessageText, setEditingMessageText] = useState(''); // Stores the current text in the edit field
  const originalMessageTextRef = useRef(null); // To store the original text for 'Cancel'
  const textareaRef = useRef(null); // Ref for the editing textarea

  // NEW: State to store the last user query for suggested questions
  const lastUserQueryForSuggestions = useRef('');


  // Effect to scroll to the bottom of the chat when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, suggestedQuestions, similarAnimeNote]); // Also scroll when suggestions/note appear

  // Effect to adjust textarea height when editingMessageText changes
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height to recalculate
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [editingMessageText, editingMessageId]); // Re-adjust on text change or when editing starts/stops

  // Helper function to render message content, supporting arrays (for SpoilerText)
  const renderMessageContent = (content) => {
    if (Array.isArray(content)) {
      return content.map((part, i) => (
        <React.Fragment key={i}>{part}</React.Fragment>
      ));
    }
    return content;
  };

  // Function to process bot responses and render spoiler content
  const processBotResponse = (responseText) => {
    const SPOILER_REGEX = /<spoiler>(.*?)<\/spoiler>/g;
    let parts = [];
    let lastIndex = 0;
    let match;

    while ((match = SPOILER_REGEX.exec(responseText)) !== null) {
      if (match.index > lastIndex) {
        parts.push(responseText.substring(lastIndex, match.index));
      }
      // Pass the global shield state to the SpoilerText component
      parts.push(<SpoilerText key={match.index} globalShieldActive={isSpoilerShieldActive}>{match[1]}</SpoilerText>);
      lastIndex = SPOILER_REGEX.lastIndex;
    }

    if (lastIndex < responseText.length) {
      parts.push(responseText.substring(lastIndex));
    }
    return parts;
  };

  // Helper function to encapsulate the LLM interaction logic
  const processQueryAndGetResponse = async (queryToProcess) => {
    setIsLoading(true);
    setSuggestedQuestions([]); // Clear suggested questions
    setSimilarAnimeNote(null); // Clear similar anime note

    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    let botRawText = ''; // To store the plain text response from bot
    try {
      const response = await api.llm.chat(queryToProcess, signal);

      if (response) {
        botRawText = response.response; // Store raw text for suggestions
        const processedText = processBotResponse(botRawText);
        const botMessage = { sender: 'bot', text: processedText };
        setMessages(prev => [...prev, botMessage]);
      }

      // CORRECTED: Pass lastUserQueryForSuggestions.current (user's query) for suggested questions
      if (lastUserQueryForSuggestions.current) {
        const suggestionsResponse = await api.llm.getSuggestedQuestions(lastUserQueryForSuggestions.current);
        if(suggestionsResponse) {
            if (suggestionsResponse.suggested_questions) {
                setSuggestedQuestions(suggestionsResponse.suggested_questions);
            }
            if (suggestionsResponse.similar_anime_note) {
                setSimilarAnimeNote(suggestionsResponse.similar_anime_note);
            }
        }
      }
    } catch (error) {
      if (!axios.isCancel(error)) {
        const errorMessage = { sender: 'bot', text: `Sorry, something went wrong: ${error.message}` };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  // Updated: handleSendMessage now only handles new user message submission
  const handleSendMessage = async (query) => {
    if (!query || isLoading) return;

    const userMessage = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMessage]); // Add the user's message immediately
    lastUserQueryForSuggestions.current = query; // Store the user's query here
    setInputValue(''); // Clear input after sending

    // Call the new helper to handle the actual LLM interaction
    await processQueryAndGetResponse(query);
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort('User stopped generation');
      console.log('LLM generation stopped by user.');
      setIsLoading(false);
      setMessages(prev => [...prev, { sender: 'bot', text: 'Generation stopped.' }]);
    }
  };

  // Updated: Handle editing a message in-place
  const handleEditMessage = (messageText, index) => {
    if (isLoading) {
      handleStopGeneration(); // If LLM is generating, stop it first
    }
    setIsSpeechActive(false); // Stop speech recognition if active

    // If another message is already being edited, save it first
    if (editingMessageId !== null && editingMessageId !== index) {
      handleSaveEdit(editingMessageId); // Auto-save the previous edit
    }

    // Convert potential array of React elements (from SpoilerText) to plain string for editing
    const textToEdit = Array.isArray(messageText) ?
                       messageText.map(part => typeof part === 'string' ? part : '').join('') :
                       messageText;

    setEditingMessageId(index);
    setEditingMessageText(textToEdit);
    originalMessageTextRef.current = textToEdit; // Store original for cancel
  };

  // Updated: Handle saving an edited message and resubmitting it to LLM
  const handleSaveEdit = (index) => {
    // Only save if text has changed
    if (editingMessageText.trim() !== originalMessageTextRef.current.trim()) {
      // First, update the message in the chat history
      setMessages(prevMessages =>
        prevMessages.map((msg, msgIndex) =>
          msgIndex === index ? { ...msg, text: editingMessageText } : msg
        )
      );
      // Then, process the *edited* message as a new query to the LLM
      // This will add a new AI response below the original edited message
      // Note: For suggestions, this edited text IS the new 'user query'
      lastUserQueryForSuggestions.current = editingMessageText; // Update the last user query for suggestions
      processQueryAndGetResponse(editingMessageText);
    } else {
      console.log("No changes detected in edited message, not resubmitting.");
    }

    // Reset editing states regardless of whether text changed or not
    setEditingMessageId(null);
    setEditingMessageText('');
    originalMessageTextRef.current = null;
  };

  // New: Handle canceling an edit
  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditingMessageText(''); // Clear the editing text
    originalMessageTextRef.current = null; // Clear original text
  };

  // Handle "Enter" key press for editing textarea
  const handleEditKeyDown = (e, index) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Submit on Enter, allow Shift+Enter for new line
      e.preventDefault(); // Prevent default newline behavior
      handleSaveEdit(index);
    }
  };


  const handleFormSubmit = (e) => {
    e.preventDefault();
    // If a message is being edited and the main input is empty, treat this as a save action
    if (editingMessageId !== null && inputValue.trim() === '') {
      handleSaveEdit(editingMessageId);
    } else if (inputValue.trim()) {
      // Otherwise, if there's text in the main input, send it as a new message
      handleSendMessage(inputValue);
    }
    // If editingMessageId is null and inputValue is empty, do nothing (e.g., pressing Enter on an empty field)
  };

  // Handle Copy functionality
  const handleCopy = (text, messageIndex) => {
    // Convert text to plain string if it's an array of React elements
    const textToCopy = Array.isArray(text) ? text.map(part => typeof part === 'string' ? part : '').join('') : text;

    // Use document.execCommand('copy') as a fallback for navigator.clipboard
    // This is safer for iframe environments where clipboard access might be restricted.
    const tempTextArea = document.createElement('textarea');
    tempTextArea.value = textToCopy;
    document.body.appendChild(tempTextArea);
    tempTextArea.select(); // Select the text
    try {
      document.execCommand('copy'); // Execute copy command
      setCopiedMessageId(messageIndex);
      setTimeout(() => setCopiedMessageId(null), 2000); // Clear "Copied!" after 2 seconds
    } catch (err) {
      console.error('Failed to copy text: ', err);
      // Fallback for older browsers or specific environments, could use alert() here
      // but we avoid alert() due to framework restrictions. Log to console instead.
    } finally {
      document.body.removeChild(tempTextArea); // Remove the temporary textarea
    }
  };


  // Callback from SpeechToText component when a transcript is available
  const handleSpeechToTextTranscript = (transcript) => {
    setInputValue(transcript); // Put the transcribed text into the input field
    // The SpeechToText component's onend event will handle setting setIsSpeechActive(false)
  };

  // Callback from SpeechToText component for recording status changes
  const handleSpeechRecordingStatusChange = (status) => {
    setIsSpeechActive(status);
    // If recording stops, and there's content in the input, clear any previous speech errors.
    // This assumes the user successfully spoke and the error is resolved.
    if (!status && inputValue) {
      setSpeechRecognitionError('');
    }
  };

  // Callback from SpeechToText component for errors
  const handleSpeechError = (errorMsg) => {
    setSpeechRecognitionError(errorMsg);
    // Automatically stop speech recognition if an error occurs
    setIsSpeechActive(false);
  };

  // Handler for the microphone button click
  const handleMicrophoneClick = () => {
    if (isSpeechActive) {
      // If currently active, toggle it off (this will trigger SpeechToText to stop)
      setIsSpeechActive(false);
    } else {
      // If not active, toggle it on
      if (isLoading) {
        // If LLM is currently generating a response, stop it first
        handleStopGeneration();
      }
      setInputValue(''); // Clear current input before starting speech input
      setSpeechRecognitionError(''); // Clear any previous speech errors
      setIsSpeechActive(true); // Signal to SpeechToText to start recording
    }
  };

  const handleClearChat = () => {
    setMessages([{ sender: 'bot', text: 'Welcome to Mushi AI. How can I help you today?' }]);
    setSuggestedQuestions([]);
    setSimilarAnimeNote(null); // Clear similar anime note
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
    lastUserQueryForSuggestions.current = ''; // Clear stored user query as well
  };


  return (
    <div className="flex flex-col h-full">
      {/* New: Chat Title */}
      <h2 className="text-xl font-bold text-white mb-4 text-center">Mushi AI Chat</h2>

      {/* Chat Messages Area */}
      <div ref={messagesEndRef} className="flex-grow overflow-y-auto p-4 space-y-4 custom-scrollbar pb-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
            {msg.sender === 'bot' && (
              <>
                <Bot className="w-6 h-6 text-indigo-400 flex-shrink-0" />
                {/* Increased max-w to max-w-2xl and added whitespace-pre-wrap for bot messages */}
                <div className={`max-w-2xl p-4 rounded-lg bg-gray-700 text-gray-200`}>
                  <p className="text-base leading-relaxed font-sans whitespace-pre-wrap">
                    {renderMessageContent(msg.text)}
                  </p>
                </div>
                {/* Copy button for bot messages */}
                <button
                  onClick={() => handleCopy(msg.text, index)}
                  className="p-1 rounded-full text-gray-400 hover:text-white hover:bg-gray-600 flex-shrink-0"
                  title="Copy message"
                >
                  <Copy size={16} />
                </button>
                {copiedMessageId === index && <span className="text-xs text-green-400 ml-1">Copied!</span>}
              </>
            )}
            {msg.sender === 'user' && (
              <>
                {/* Conditional rendering for editing user messages */}
                {editingMessageId === index ? (
                  <div className={`max-w-xl p-4 rounded-lg bg-indigo-600 text-white`}>
                    <textarea
                      ref={textareaRef} // Assign ref to textarea
                      className="w-full bg-indigo-700 text-white p-2 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400 overflow-hidden" // Added overflow-hidden to prevent scrollbar during auto-resize
                      value={editingMessageText}
                      onChange={(e) => setEditingMessageText(e.target.value)}
                      onKeyDown={(e) => handleEditKeyDown(e, index)} // Handle Enter key
                      rows={1} // Start with 1 row, height adjusted by useEffect
                    />
                  </div>
                ) : (
                  <div className={`max-w-xl p-4 rounded-lg bg-indigo-600 text-white`}>
                    <p className="text-base leading-relaxed font-sans">
                      {renderMessageContent(msg.text)}
                    </p>
                  </div>
                )}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <User className="w-6 h-6 text-gray-400" />
                  {/* Conditional rendering for Edit/Save/Cancel buttons */}
                  {editingMessageId === index ? (
                    <>
                      <button
                        onClick={() => handleSaveEdit(index)}
                        className="p-1 rounded-full text-gray-400 hover:text-white hover:bg-gray-600"
                        title="Save changes"
                      >
                        {/* Checkmark icon for Save */}
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check"><path d="M20 6 9 17l-5-5"/></svg>
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="p-1 rounded-full text-gray-400 hover:text-white hover:bg-gray-600"
                        title="Cancel edit"
                      >
                        <XCircle size={16} />
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleEditMessage(msg.text, index)}
                      className="p-1 rounded-full text-gray-400 hover:text-white hover:bg-gray-600"
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
        {/* Processing Indicator for LLM Response */}
        {isLoading && <div className="text-center text-gray-400">Mushi is thinking...</div>}
      </div>

      {/* Suggested Questions */}
      <QuestionPrompts questions={suggestedQuestions} onQuestionClick={handleSendMessage} />

      {/* Similar Anime Note */}
      {similarAnimeNote && (
        <div className="px-4 py-3 border border-blue-500 rounded-lg mb-4 bg-gray-800 text-blue-300 text-sm">
          {similarAnimeNote}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleFormSubmit} className="flex items-center gap-2 border-t border-gray-700 pt-4">
        {/* Clear Chat Button */}
        <button
          type="button"
          onClick={handleClearChat}
          className="p-2 rounded-full bg-gray-700 text-gray-400 hover:text-white hover:bg-red-600 transition-colors duration-200 flex items-center justify-center"
          title="Clear Chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-trash-2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
        </button>

        {/* Spoiler Shield Toggle Button */}
        <button
          type="button"
          onClick={() => setIsSpoilerShieldActive(prev => !prev)}
          className={`p-2 rounded-full transition-colors duration-200 flex items-center justify-center ${
            isSpoilerShieldActive ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-400 hover:text-white hover:bg-gray-600'
          }`}
          title={isSpoilerShieldActive ? "Spoiler Shield: Active" : "Spoiler Shield: Inactive"}
        >
          {isSpoilerShieldActive ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>

        {/* Microphone Button */}
        <button
          type="button"
          onClick={handleMicrophoneClick}
          className={`p-2 rounded-full transition-colors duration-200 flex items-center justify-center ${
            isSpeechActive ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-400 hover:text-white hover:bg-gray-600'
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
          className="flex-grow bg-gray-700 rounded-full py-2 px-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          disabled={isLoading || isSpeechActive || editingMessageId !== null} // Disable if editing a message in-place
        />

        {/* Conditional rendering for Stop button (when LLM is loading) or Send button */}
        {isLoading ? (
          <button
            type="button"
            onClick={handleStopGeneration}
            className="bg-red-600 hover:bg-red-700 text-white p-2 rounded-full transition-colors duration-200 flex items-center justify-center"
            title="Stop generation"
          >
            <XCircle size={20} />
          </button>
        ) : (
          <button
            type="submit"
            className="bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-full transition-colors duration-200 flex items-center justify-center"
            disabled={!inputValue.trim() && editingMessageId === null || isSpeechActive} // Disable if empty and not editing, or if speech active
            title={editingMessageId !== null ? "Save Edited Question" : "Send New Question"}
          >
            {editingMessageId !== null ?
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucuce-check"><path d="M20 6 9 17l-5-5"/></svg>
              : <Send size={20} />
            }
          </button>
        )}
      </form>
      {/* Recording in progress indicator */}
      {isSpeechActive && <p className="text-center text-indigo-400 text-sm mt-2">Recording in progress... Speak now!</p>}
      {/* Display speech recognition errors */}
      {speechRecognitionError && <p className="text-center text-red-400 text-sm mt-2">{speechRecognitionError}</p>}


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
