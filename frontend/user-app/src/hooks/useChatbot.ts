/**
 * useChatbot Hook
 * Lógica de negocio para el chatbot
 */

import { useState, useCallback } from 'react';
import type { ChatMessage, FAQItem } from '../types/chatbot.types';
import { WELCOME_MESSAGE, FALLBACK_MESSAGE, faqData } from '../data/faqData';
import { findBestMatch } from '../utils/faqMatcher';

let messageIdCounter = 0;

export function useChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const generateMessageId = useCallback(() => {
    return `msg-${Date.now()}-${messageIdCounter++}`;
  }, []);

  const addMessage = useCallback((text: string, sender: 'user' | 'bot') => {
    const newMessage: ChatMessage = {
      id: generateMessageId(),
      text,
      sender,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  }, [generateMessageId]);

  const openChat = useCallback(() => {
    setIsOpen(true);
    if (messages.length === 0) {
      addMessage(WELCOME_MESSAGE, 'bot');
    }
  }, [messages.length, addMessage]);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    addMessage(text, 'user');

    // Show typing indicator
    setIsTyping(true);

    // Simulate bot thinking time
    await new Promise(resolve => setTimeout(resolve, 600));

    // Find best matching FAQ
    const matchResult = findBestMatch(text, faqData);
    const botResponse = matchResult.found && matchResult.faq
      ? matchResult.faq.answer
      : FALLBACK_MESSAGE;

    // Add bot response
    addMessage(botResponse, 'bot');

    // Hide typing indicator
    setIsTyping(false);
  }, [addMessage]);

  const selectFAQ = useCallback((faq: FAQItem) => {
    // Add FAQ question as user message
    addMessage(faq.question, 'user');
    // Add FAQ answer as bot response (immediately, no typing delay)
    addMessage(faq.answer, 'bot');
  }, [addMessage]);

  return {
    messages,
    isOpen,
    isTyping,
    openChat,
    closeChat,
    sendMessage,
    selectFAQ
  };
}
