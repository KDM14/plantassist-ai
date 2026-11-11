import Header from './components/Header';
import ChatInterface from './components/ChatInterface';
import { useChat } from './hooks/useChat';

export default function App() {
  const { messages, isLoading, ask, clearChat } = useChat();

  return (
    <div className="flex flex-col h-screen bg-slate-950 overflow-hidden">
      <Header onNewChat={clearChat} />
      <main className="flex-1 overflow-hidden">
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onSend={ask}
          onClear={clearChat}
        />
      </main>
    </div>
  );
}
