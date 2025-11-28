import { AxiosError } from 'axios';

export interface ApiError {
  message: string;
  statusCode?: number;
  error?: string;
}

/**
 * Parse API errors into user-friendly messages
 */
export function parseApiError(error: unknown): ApiError {
  // Handle Axios errors
  if (error instanceof Error && 'isAxiosError' in error) {
    const axiosError = error as AxiosError<{ message?: string; error?: string }>;

    // Network error (offline, server unreachable)
    if (!axiosError.response) {
      return {
        message: 'You appear to be offline. Please check your internet connection.',
        statusCode: 0,
      };
    }

    const status = axiosError.response.status;
    const data = axiosError.response.data;

    // Map status codes to user-friendly messages
    switch (status) {
      case 400:
        return {
          message: data?.message || 'Invalid request. Please check your input.',
          statusCode: 400,
          error: 'Bad Request',
        };

      case 401:
        return {
          message: data?.message || 'Invalid credentials or session expired.',
          statusCode: 401,
          error: 'Unauthorized',
        };

      case 403:
        return {
          message: data?.message || 'You do not have permission to perform this action.',
          statusCode: 403,
          error: 'Forbidden',
        };

      case 404:
        return {
          message: data?.message || 'The requested resource was not found.',
          statusCode: 404,
          error: 'Not Found',
        };

      case 409:
        return {
          message: data?.message || 'A conflict occurred. This resource may already exist.',
          statusCode: 409,
          error: 'Conflict',
        };

      case 422:
        return {
          message: data?.message || 'Validation error. Please check your input.',
          statusCode: 422,
          error: 'Unprocessable Entity',
        };

      case 500:
      case 502:
      case 503:
      case 504:
        return {
          message: 'Something went wrong on our end. Please try again later.',
          statusCode: status,
          error: 'Server Error',
        };

      default:
        return {
          message: data?.message || 'An unexpected error occurred. Please try again.',
          statusCode: status,
          error: data?.error || 'Unknown Error',
        };
    }
  }

  // Handle generic errors
  if (error instanceof Error) {
    return {
      message: error.message,
    };
  }

  // Fallback for unknown errors
  return {
    message: 'An unexpected error occurred. Please try again.',
  };
}
