import { Button } from '@/components/livekit/button';

function SwiggyLogo() {
  return (
    <div className="mb-6 flex flex-col items-center">
      <div className="w-20 h-20 bg-orange-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
        <svg
          width="48"
          height="48"
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M24 8C16.268 8 10 14.268 10 22C10 25.866 11.582 29.358 14.142 31.918L24 42L33.858 31.918C36.418 29.358 38 25.866 38 22C38 14.268 31.732 8 24 8ZM24 28C20.686 28 18 25.314 18 22C18 18.686 20.686 16 24 16C27.314 16 30 18.686 30 22C30 25.314 27.314 28 24 28Z"
            fill="white"
          />
        </svg>
      </div>
      <h1 className="text-3xl font-bold text-orange-600 mb-1">Swiggy Partner Voice AI</h1>
      <p className="text-orange-500 text-sm font-medium">Powered by Murf Falcon TTS</p>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="bg-gradient-to-br from-gray-900 via-gray-800 to-black min-h-screen">
      <section className="flex flex-col items-center justify-center text-center pt-24 px-6">
        <SwiggyLogo />

        <div className="max-w-2xl mx-auto px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Talk to Alex - Your Swiggy Partnership Assistant
          </h2>
          <p className="text-gray-300 max-w-prose leading-8 mb-3 text-lg">
            I can help answer your questions about partnering with Swiggy, our pricing, onboarding process, and everything you need to grow your business with India's leading delivery platform.
          </p>
          <p className="text-sm text-gray-400 mb-10">
            Just click below and start talking. I'm here to help!
          </p>
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-6 w-80 h-16 text-xl font-bold bg-orange-500 hover:bg-orange-600 text-white rounded-2xl shadow-2xl shadow-orange-500/30 transition-all duration-200 hover:scale-105 hover:shadow-orange-500/50"
        >
          {startButtonText}
        </Button>

        <div className="mt-16 bg-gray-800/60 backdrop-blur-sm rounded-3xl shadow-xl border border-gray-700/50 p-8 max-w-4xl mx-6">
          <h3 className="text-xl font-bold text-white mb-6">What I can help with:</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-base">
            <div className="flex items-start">
              <span className="text-orange-500 mr-3 text-lg">●</span>
              <span className="text-gray-200">Partnership details and pricing</span>
            </div>
            <div className="flex items-start">
              <span className="text-orange-500 mr-3 text-lg">●</span>
              <span className="text-gray-200">Onboarding process</span>
            </div>
            <div className="flex items-start">
              <span className="text-orange-500 mr-3 text-lg">●</span>
              <span className="text-gray-200">Product offerings</span>
            </div>
            <div className="flex items-start">
              <span className="text-orange-500 mr-3 text-lg">●</span>
              <span className="text-gray-200">Technical requirements</span>
            </div>
            <div className="flex items-start">
              <span className="text-orange-500 mr-3 text-lg">●</span>
              <span className="text-gray-200">Payment settlements</span>
            </div>
            <div className="flex items-start">
              <span className="text-orange-500 mr-3 text-lg">●</span>
              <span className="text-gray-200">Marketing support</span>
            </div>
          </div>
        </div>
      </section>

      <div className="fixed bottom-6 left-0 flex w-full items-center justify-center">
        <p className="text-gray-400 max-w-prose pt-1 text-xs leading-6 font-normal text-pretty md:text-sm">
          Built with Murf Falcon - The Fastest TTS API | Day 5 of #10DaysofAIVoiceAgents Challenge
        </p>
      </div>
    </div>
  );
};
