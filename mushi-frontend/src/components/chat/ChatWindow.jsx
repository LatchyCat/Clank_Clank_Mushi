// mushi-frontend/src/components/chat/ChatWindow.jsx
import React, { useState, useRef, useEffect } from 'react';
import { api } from '../../services/api';
import QuestionPrompts from './QuestionPrompts';
import { Send, User, XCircle, Edit3, Mic, StopCircle, Copy, Trash2, Check, BrainCircuit } from 'lucide-react';
import SpeechToText from './SpeechToText';
import { Link } from 'react-router-dom';
import SpoilerText from './SpoilerText';

const snailImages = {
    default: '/mushi_snail_luffy.png',
    happy: '/mushi_snail_jump_happy.png',
    excited: '/mushi_snail_sabo.png',
    thinking: '/mushi_snail_weirdo.png',
    giggle: '/mushi_snail_nami.png',
    curious: '/mushi_snail_chopper.png',
    error: '/mushi_snail_cry.png'
};

const getSnailIcon = (mood = 'default') => snailImages[mood] || snailImages.default;

const MushiAvatar = ({ src }) => (
  <div className="w-10 h-10 rounded-full flex-shrink-0 bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-lg">
    <img src={src} alt="Mushi Icon" className="w-9 h-9 object-contain" />
  </div>
);

const UserAvatar = () => (
  <div className="w-10 h-10 rounded-full flex-shrink-0 bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center shadow-lg">
      <User className="w-6 h-6 text-white"/>
  </div>
);


const ResolvedLink = ({ title }) => {
    const [linkData, setLinkData] = useState({ title: title, url: null });
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;
        api.llm.resolveLink(title).then(data => {
            if (isMounted && data) setLinkData(data);
        }).catch(error => {
            console.error("Error resolving link for:", title, error.message);
            setLinkData({ title, url: `/search?keyword=${encodeURIComponent(title)}` });
        }).finally(() => {
            if (isMounted) setIsLoading(false);
        });
        return () => { isMounted = false; };
    }, [title]);

    if (isLoading) {
        return <span className="text-pink-400/50">{title}</span>;
    }

    return (
      <a
        href={linkData.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-pink-400 hover:text-pink-300 underline font-semibold"
      >
        {linkData.title}
      </a>
    );
};

const MessageRenderer = ({ text }) => {
    const parts = text.split(/(\[LINK:.*?\]|<spoiler>.*?<\/spoiler>)/g);

    return (
        <div className="markdown-content">
            {parts.map((part, index) => {
                const linkMatch = part.match(/\[LINK:(.*?)\]/);
                if (linkMatch) {
                    const title = linkMatch[1];
                    return <ResolvedLink key={`${index}-${title}`} title={title} />;
                }

                const spoilerMatch = part.match(/<spoiler>(.*?)<\/spoiler>/s);
                if (spoilerMatch) {
                    return <SpoilerText key={index}>{spoilerMatch[1]}</SpoilerText>;
                }

                return <span key={index} className="whitespace-pre-wrap">{part}</span>;
            })}
        </div>
    );
};

function ChatWindow({ initialQuery }) {
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'Welcome to Mushi AI. How can I help you today, Senpai? I can search my knowledge base for all kinds of anime info!', id: 'welcome-message', iconSrc: getSnailIcon('happy') }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [suggestedQuestions, setSuggestedQuestions] = useState([]);
    const [isSpeechActive, setIsSpeechActive] = useState(false);
    const [speechRecognitionError, setSpeechRecognitionError] = useState('');
    const [currentStreamingBotMessage, setCurrentStreamingBotMessage] = useState('');
    const [currentBotIcon, setCurrentBotIcon] = useState(getSnailIcon());
    const [copiedMessageId, setCopiedMessageId] = useState(null);
    const [editingMessageId, setEditingMessageId] = useState(null);
    const [editingMessageText, setEditingMessageText] = useState('');

    const abortControllerRef = useRef(null);
    const chatContainerRef = useRef(null);
    const initialQueryProcessed = useRef(false);

    useEffect(() => {
        chatContainerRef.current?.scrollTo({ top: chatContainerRef.current.scrollHeight, behavior: 'smooth' });
    }, [messages, currentStreamingBotMessage]);

    useEffect(() => {
        if (initialQuery && !initialQueryProcessed.current) {
            handleSendMessage(initialQuery);
            initialQueryProcessed.current = true;
        }
    }, [initialQuery]);

    const processQueryAndGetResponse = async (queryToProcess) => {
        setSuggestedQuestions([]);
        setIsLoading(true);
        const history = messages.slice(-4).map(m => ({ sender: m.sender, text: m.text }));
        const userMessageId = `user-${Date.now()}`;
        setMessages(prev => [...prev, { sender: 'user', text: queryToProcess, id: userMessageId }]);
        setCurrentStreamingBotMessage('');

        let accumulatedBotResponse = '';
        let finalBotIcon = getSnailIcon('thinking');
        setCurrentBotIcon(finalBotIcon);

        abortControllerRef.current = new AbortController();
        const signal = abortControllerRef.current.signal;

        try {
            await api.llm.chat(queryToProcess, history, (chunk) => {
                if (signal.aborted) return;

                if (chunk.type === 'mood') {
                    finalBotIcon = getSnailIcon(chunk.content);
                    setCurrentBotIcon(finalBotIcon);
                } else if (chunk.type === 'text') {
                    accumulatedBotResponse += chunk.content;
                } else if (chunk.type === 'error') {
                     accumulatedBotResponse += `\n\n**Error:** ${chunk.content}`;
                     finalBotIcon = getSnailIcon('error');
                     setCurrentBotIcon(finalBotIcon);
                }
                setCurrentStreamingBotMessage(accumulatedBotResponse);
            }, signal);

            if (!signal.aborted && accumulatedBotResponse) {
                const suggestionPayload = { user_query: queryToProcess, mushi_response: accumulatedBotResponse };
                const suggestionsResponse = await api.llm.getSuggestedQuestions(suggestionPayload);
                if (suggestionsResponse) setSuggestedQuestions(suggestionsResponse.suggested_questions || []);
            }
        } catch (error) {
            let errorMessageText = `Sorry, something went wrong: ${error.message}.`;
            if (error.name === 'AbortError') errorMessageText = "Mushi stopped generating, desu!";
            accumulatedBotResponse = errorMessageText;
            finalBotIcon = getSnailIcon('error');
        } finally {
            if (accumulatedBotResponse) {
                setMessages(prev => [...prev, { sender: 'bot', text: accumulatedBotResponse, id: `bot-final-${Date.now()}`, iconSrc: finalBotIcon }]);
            }
            setCurrentStreamingBotMessage('');
            setIsLoading(false);
            abortControllerRef.current = null;
        }
    };

    const handleSendMessage = async (query) => { if (!query.trim() || isLoading) return; setInputValue(''); await processQueryAndGetResponse(query); };
    const handleStopGeneration = () => { if (abortControllerRef.current) { abortControllerRef.current.abort('User stopped generation'); } };
    const handleEditMessage = (id) => { const msg = messages.find(m => m.id === id); if (msg) { setEditingMessageId(id); setEditingMessageText(msg.text); } };
    const handleSaveEdit = () => { processQueryAndGetResponse(editingMessageText); setEditingMessageId(null); setEditingMessageText(''); };
    const handleCancelEdit = () => { setEditingMessageId(null); setEditingMessageText(''); };
    const handleCopy = (text, id) => { navigator.clipboard.writeText(text).then(() => { setCopiedMessageId(id); setTimeout(() => setCopiedMessageId(null), 2000); }); };
    const handleClearChat = () => { setMessages([{ sender: 'bot', text: 'Welcome to Mushi AI. How can I help you today?', id: 'welcome-message', iconSrc: getSnailIcon('happy') }]); setSuggestedQuestions([]); handleStopGeneration(); };

    return (
        <div className="flex flex-col h-full bg-neutral-950/50 p-4 rounded-lg shadow-2xl border border-white/10">
            <div ref={chatContainerRef} className="flex-grow chat-log-container p-4 space-y-6 custom-scrollbar pb-4 rounded-xl bg-black/20 border border-white/10">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex items-start gap-4 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                        {msg.sender === 'bot' ? (
                            <>
                                <MushiAvatar src={msg.iconSrc} />
                                <div className="group relative max-w-2xl p-4 rounded-xl bg-gradient-to-br from-neutral-800 to-neutral-700 text-gray-200 shadow-md">
                                    <MessageRenderer text={msg.text} />
                                    <button onClick={() => handleCopy(msg.text, msg.id)} className="absolute -top-2 -right-2 p-1.5 rounded-full text-gray-400 bg-neutral-800 hover:text-white hover:bg-neutral-700 opacity-0 group-hover:opacity-100 transition-opacity" title="Copy">
                                        {copiedMessageId === msg.id ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                                    </button>
                                </div>
                            </>
                        ) : (
                             <>
                                {editingMessageId === msg.id ? (
                                    <div className="w-full p-2 rounded-xl bg-purple-900/50 text-white shadow-md border border-purple-600">
                                        <textarea className="w-full bg-transparent p-2 rounded-lg resize-none focus:outline-none" value={editingMessageText} onChange={(e) => setEditingMessageText(e.target.value)} rows={3} autoFocus/>
                                        <div className="flex justify-end gap-2 mt-2">
                                            <button onClick={handleSaveEdit} className="p-2 rounded-full text-green-400 hover:bg-green-600/20" title="Save"><Send size={16} /></button>
                                            <button onClick={handleCancelEdit} className="p-2 rounded-full text-red-400 hover:bg-red-600/20" title="Cancel"><XCircle size={16} /></button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="group relative max-w-xl p-4 rounded-xl bg-gradient-to-br from-purple-600 to-fuchsia-600 text-white shadow-md">
                                        <p className="text-base leading-relaxed font-sans">{msg.text}</p>
                                        <div className="absolute -top-2 -right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button onClick={() => handleCopy(msg.text, msg.id)} className="p-1.5 rounded-full text-gray-200 bg-purple-700 hover:text-white hover:bg-purple-600" title="Copy">
                                                {copiedMessageId === msg.id ? <Check size={14} className="text-lime-300" /> : <Copy size={14} />}
                                            </button>
                                            <button onClick={() => handleEditMessage(msg.id)} className="p-1.5 rounded-full text-gray-200 bg-purple-700 hover:text-white hover:bg-purple-600" title="Edit">
                                                <Edit3 size={14} />
                                            </button>
                                        </div>
                                    </div>
                                )}
                                <UserAvatar />
                            </>
                        )}
                    </div>
                ))}
                {currentStreamingBotMessage && (
                    <div className="flex items-start gap-4">
                        <MushiAvatar src={currentBotIcon} />
                        <div className="max-w-2xl p-4 rounded-xl bg-gradient-to-br from-neutral-800 to-neutral-700 text-gray-200 shadow-md">
                            <MessageRenderer text={currentStreamingBotMessage} />
                        </div>
                    </div>
                )}
                {isLoading && !currentStreamingBotMessage &&
                  <div className="flex justify-center items-center gap-2 text-purple-400 animate-pulse">
                      <BrainCircuit size={16} /> Mushi is thinking...
                  </div>
                }
            </div>

            <div className="mt-2 mb-4">
              <QuestionPrompts questions={suggestedQuestions} onQuestionClick={handleSendMessage} />
            </div>

            {speechRecognitionError && <div className="text-center text-red-400 text-xs mb-2">{speechRecognitionError}</div>}

            <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(inputValue); }} className="flex items-center gap-3 border-t border-white/10 pt-4">
                <button type="button" onClick={handleClearChat} className="p-3 rounded-full text-gray-400 hover:text-white hover:bg-red-500/50 transition-colors" title="Clear Chat"><Trash2 size={20} /></button>
                <button type="button" onClick={() => setIsSpeechActive(prev => !prev)} className={`p-3 rounded-full text-gray-400 hover:text-white transition-colors ${isSpeechActive ? 'bg-red-500/80' : 'bg-white/10 hover:bg-purple-500/50'}`} title="Toggle Speech-to-Text">
                    {isSpeechActive ? <StopCircle size={20}/> : <Mic size={20}/>}
                </button>

                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder={isLoading ? "Mushi is thinking..." : (isSpeechActive ? "Listening..." : "Ask Mushi anything...")}
                    className="flex-grow bg-white/5 rounded-full py-3 px-5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500 border border-white/20 transition-all duration-300"
                    disabled={isSpeechActive}
                />

                {isLoading ? (
                    <button type="button" onClick={handleStopGeneration} className="bg-red-600 hover:bg-red-700 text-white p-3 rounded-full" title="Stop Generation"><XCircle size={20} /></button>
                ) : (
                    <button type="submit" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white p-3 rounded-full disabled:opacity-50 disabled:cursor-not-allowed" disabled={!inputValue.trim() || isSpeechActive} title="Send Message"><Send size={20} /></button>
                )}
            </form>
        </div>
    );
}

export default ChatWindow;
