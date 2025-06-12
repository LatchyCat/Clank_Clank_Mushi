// mushi-frontend/src/views/LandingPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Bot, Compass, BarChart, Swords } from 'lucide-react'; // Using lucide-react for icons

// A simple feature card component for reusability
const FeatureCard = ({ icon, title, description }) => (
  <div className="bg-gray-800 p-6 rounded-lg shadow-lg transform hover:scale-105 transition-transform duration-300">
    <div className="flex items-center mb-4">
      {icon}
      <h3 className="text-xl font-bold text-blue-400 ml-3">{title}</h3>
    </div>
    <p className="text-gray-300">{description}</p>
  </div>
);

function LandingPage() {
  const features = [
    {
      icon: <Bot size={28} className="text-blue-400" />,
      title: 'The "Whispering Snail" AI Chat',
      description: 'Ask anything about anime—from plot summaries to complex theories—and get intelligent, context-aware answers.',
    },
    {
      icon: <Compass size={28} className="text-blue-400" />,
      title: 'The "Lore Navigator"',
      description: 'Highlight any term or name you don\'t recognize in an article for an instant, AI-powered explanation.',
    },
    {
      icon: <BarChart size={28} className="text-blue-400" />,
      title: 'The "Trendspotter"',
      description: 'Go beyond headlines with AI insights into fan sentiment, community buzz, and predictions on what\'s next in anime.',
    },
    {
      icon: <Swords size={28} className="text-blue-400" />,
      title: 'The "Debate Arena"',
      description: 'Settle arguments by posing "what-if" scenarios to the AI, which provides balanced perspectives based on established lore.',
    },
  ];

  return (
    <div className="bg-gray-900 text-gray-100 font-inter">
      <div className="container mx-auto px-6 py-12">
        <header className="text-center mb-12">
          <div className="flex justify-center items-center mb-4">
            <Sparkles className="text-yellow-400" size={48} />
            <h1 className="text-5xl font-extrabold ml-4">Clank Clank Mushi</h1>
          </div>
          <p className="text-xl text-gray-300 mt-2">Your Personal Anime Intelligence Hub</p>
        </header>

        <section className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl font-bold mb-4 text-blue-300">What is Clank Clank Mushi?</h2>
          <p className="text-lg text-gray-300 leading-relaxed">
            It’s not another streaming site—it's your private, AI-powered portal to the anime world. Running on your own computer, it aggregates the latest anime news and uses a powerful AI to help you explore, understand, and discuss every facet of your favorite shows and the industry itself.
          </p>
        </section>

        <section className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-8 text-blue-300">Features That Power Your Fandom</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </section>

        <footer className="text-center">
          <p className="text-lg text-gray-400 mb-6">Ready to dive deeper than ever before?</p>
          <Link
            to="/app"
            className="inline-block bg-blue-600 text-white font-bold text-xl py-4 px-10 rounded-lg shadow-lg hover:bg-blue-700 transition-all duration-300 transform hover:scale-110"
          >
            Enter the App
          </Link>
        </footer>
      </div>
    </div>
  );
}

export default LandingPage;
