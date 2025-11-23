import { Button } from '@/components/livekit/button';

function WelcomeImage() {
  return (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-fg0 mb-6 size-28"
    >
      {/* Coffee cup */}
      <path
        d="M30 35 C30 35, 28 32, 30 30 C32 28, 34 30, 34 30"
        stroke="currentColor"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M40 35 C40 35, 38 32, 40 30 C42 28, 44 30, 44 30"
        stroke="currentColor"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M50 35 C50 35, 48 32, 50 30 C52 28, 54 30, 54 30"
        stroke="currentColor"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
      />
      {/* Cup body */}
      <path
        d="M25 40 L30 90 C30 95, 32 98, 37 98 L47 98 C52 98, 54 95, 54 90 L59 40 Z"
        fill="currentColor"
        opacity="0.8"
      />
      {/* Cup handle */}
      <path
        d="M59 50 C65 50, 68 53, 68 60 C68 67, 65 70, 59 70"
        stroke="currentColor"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
      />
      {/* Saucer */}
      <ellipse cx="42" cy="100" rx="22" ry="4" fill="currentColor" opacity="0.6"/>
    </svg>
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
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center px-4">
        <WelcomeImage />

        <h1 className="text-foreground text-4xl md:text-5xl font-bold mb-3">
          Prashant&apos;s Coffee Shop
        </h1>

        <p className="text-foreground max-w-prose pt-1 leading-7 font-medium text-lg mb-2">
          Your friendly AI barista is ready to take your order
        </p>

        <p className="text-muted-foreground max-w-md text-sm leading-6 mb-8">
          Order delicious coffee drinks through voice. Choose from espresso, americano, cappuccino, latte, mocha, and cold brew. Available in small, medium, or large.
        </p>

        <Button variant="primary" size="lg" onClick={onStartCall} className="mt-2 w-72 font-mono text-base py-6">
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm px-4">
          Powered by LiveKit Voice AI •{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
            className="underline"
          >
            Learn more
          </a>
        </p>
      </div>
    </div>
  );
};
