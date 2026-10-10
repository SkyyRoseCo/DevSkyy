/**
 * Error Boundary Component
 * Catches JavaScript errors in child component tree and displays fallback UI
 * Implements react-error-boundary pattern with SkyyRose branding
 *
 * @author DevSkyy Platform Team
 * @version 1.0.0
 */

import React, { Component, ReactNode } from 'react';

// SkyyRose Brand Colors
const COLORS = {
  roseGold: '#B76E79',
  roseGoldHover: '#A05D68',
  roseGoldLight: '#D4A5AE',
  black: '#1A1A1A',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  mediumGray: '#CCCCCC',
  darkGray: '#666666',
  errorBg: '#FFF5F5',
  errorBorder: '#FED7D7',
};

/**
 * Props for ErrorFallback component
 */
export interface ErrorFallbackProps {
  /** The error that was thrown */
  error: Error;
  /** Function to reset the error boundary and retry */
  resetErrorBoundary: () => void;
  /** Optional custom title */
  title?: string;
  /** Optional custom message */
  message?: string;
}

/**
 * Props for ErrorBoundary component
 */
export interface ErrorBoundaryProps {
  /** Child components to render */
  children: ReactNode;
  /** Custom fallback component */
  FallbackComponent?: React.ComponentType<ErrorFallbackProps>;
  /** Callback when error is caught */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Callback when reset is triggered */
  onReset?: () => void;
  /** Custom fallback render function */
  fallbackRender?: (props: ErrorFallbackProps) => ReactNode;
}

/**
 * State for ErrorBoundary component
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Fallback Component
 * Displays a user-friendly error message with retry functionality
 */
export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetErrorBoundary,
  title = 'Something went wrong',
  message = 'We apologize for the inconvenience. Please try again.',
}) => {
  const [isHovered, setIsHovered] = React.useState(false);
  const [isSecondaryHovered, setIsSecondaryHovered] = React.useState(false);

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        padding: '32px',
        backgroundColor: COLORS.lightGray,
      }}
    >
      <div
        style={{
          maxWidth: '500px',
          width: '100%',
          backgroundColor: COLORS.white,
          borderRadius: '16px',
          padding: '48px',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
          textAlign: 'center',
        }}
      >
        {/* Error Icon */}
        <div
          style={{
            width: '80px',
            height: '80px',
            margin: '0 auto 24px',
            backgroundColor: COLORS.errorBg,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: `2px solid ${COLORS.roseGold}`,
          }}
        >
          <svg
            width='40'
            height='40'
            viewBox='0 0 24 24'
            fill='none'
            stroke={COLORS.roseGold}
            strokeWidth='2'
            strokeLinecap='round'
            strokeLinejoin='round'
          >
            <circle cx='12' cy='12' r='10' />
            <line x1='12' y1='8' x2='12' y2='12' />
            <line x1='12' y1='16' x2='12.01' y2='16' />
          </svg>
        </div>

        {/* Title */}
        <h2
          style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: COLORS.black,
            marginBottom: '12px',
            fontFamily: 'Georgia, serif',
          }}
        >
          {title}
        </h2>

        {/* Message */}
        <p
          style={{
            fontSize: '16px',
            color: COLORS.darkGray,
            marginBottom: '24px',
            lineHeight: '1.6',
          }}
        >
          {message}
        </p>

        {/* Error Details (collapsible) */}
        <details
          style={{
            marginBottom: '32px',
            textAlign: 'left',
          }}
        >
          <summary
            style={{
              cursor: 'pointer',
              fontSize: '14px',
              color: COLORS.roseGold,
              fontWeight: 600,
              marginBottom: '12px',
              outline: 'none',
            }}
          >
            View Error Details
          </summary>
          <div
            style={{
              backgroundColor: COLORS.errorBg,
              border: `1px solid ${COLORS.errorBorder}`,
              borderRadius: '8px',
              padding: '16px',
              marginTop: '8px',
            }}
          >
            <p
              style={{
                margin: '0 0 8px 0',
                fontSize: '14px',
                fontWeight: 600,
                color: COLORS.black,
              }}
            >
              {error.name}: {error.message}
            </p>
            {error.stack && (
              <pre
                style={{
                  margin: 0,
                  fontSize: '12px',
                  color: COLORS.darkGray,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: '150px',
                  overflowY: 'auto',
                  fontFamily: 'monospace',
                }}
              >
                {error.stack}
              </pre>
            )}
          </div>
        </details>

        {/* Action Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <button
            onClick={resetErrorBoundary}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            style={{
              backgroundColor: isHovered ? COLORS.roseGoldHover : COLORS.roseGold,
              color: COLORS.white,
              border: 'none',
              borderRadius: '8px',
              padding: '16px 32px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: isHovered ? '0 6px 16px rgba(183, 110, 121, 0.4)' : '0 4px 12px rgba(183, 110, 121, 0.3)',
              transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
            }}
          >
            Try Again
          </button>

          <button
            onClick={() => window.location.reload()}
            onMouseEnter={() => setIsSecondaryHovered(true)}
            onMouseLeave={() => setIsSecondaryHovered(false)}
            style={{
              backgroundColor: isSecondaryHovered ? COLORS.roseGold : 'transparent',
              color: isSecondaryHovered ? COLORS.white : COLORS.roseGold,
              border: `2px solid ${COLORS.roseGold}`,
              borderRadius: '8px',
              padding: '14px 32px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
          >
            Refresh Page
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * Error Boundary Class Component
 * Catches JavaScript errors anywhere in child component tree
 * and displays a fallback UI instead of crashing
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  /**
   * Static method to update state when error occurs
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Lifecycle method called when error is caught
   * Used for logging error information
   */
  override componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error to console in development
    console.error('ErrorBoundary caught an error:', error);
    console.error('Error info:', errorInfo);

    // Call optional onError callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  /**
   * Reset the error boundary state
   */
  resetErrorBoundary = (): void => {
    // Call optional onReset callback
    if (this.props.onReset) {
      this.props.onReset();
    }

    this.setState({
      hasError: false,
      error: null,
    });
  };

  override render(): ReactNode {
    const { hasError, error } = this.state;
    const { children, FallbackComponent, fallbackRender } = this.props;

    if (hasError && error) {
      const fallbackProps: ErrorFallbackProps = {
        error,
        resetErrorBoundary: this.resetErrorBoundary,
      };

      // Use custom fallback render function if provided
      if (fallbackRender) {
        return fallbackRender(fallbackProps);
      }

      // Use custom FallbackComponent if provided
      if (FallbackComponent) {
        return <FallbackComponent {...fallbackProps} />;
      }

      // Use default ErrorFallback
      return <ErrorFallback {...fallbackProps} />;
    }

    return children;
  }
}

/**
 * Higher-order component to wrap a component with ErrorBoundary
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
): React.FC<P> {
  const displayName = WrappedComponent.displayName || WrappedComponent.name || 'Component';

  const WithErrorBoundary: React.FC<P> = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundary.displayName = `withErrorBoundary(${displayName})`;

  return WithErrorBoundary;
}

/**
 * Hook to programmatically trigger error boundary
 * Useful for handling async errors
 */
export function useErrorHandler(): (error: Error) => void {
  const [, setError] = React.useState<Error | null>(null);

  return React.useCallback((error: Error) => {
    setError(() => {
      throw error;
    });
  }, []);
}

export default ErrorBoundary;
