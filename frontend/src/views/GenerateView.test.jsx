import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import GenerateView from './GenerateView'
import { apiClient } from '../lib/apiClient'

vi.mock('react-hot-toast', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}))

vi.mock('../lib/apiClient', () => ({
  apiClient: {
    post: vi.fn(),
  },
  getErrorMessage: (error, fallback) => error?.message || fallback,
  isRecord: (value) => value !== null && typeof value === 'object' && !Array.isArray(value),
}))

describe('GenerateView', () => {
  it('validates required fields before submit', async () => {
    const user = userEvent.setup()
    render(<GenerateView apiKey="" onGenerated={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: /generate professional assignment/i }))

    await waitFor(() => expect(apiClient.post).not.toHaveBeenCalled())
  })

  it('submits generation request with normalized payload', async () => {
    const user = userEvent.setup()
    const onGenerated = vi.fn()
    apiClient.post.mockResolvedValueOnce({ data: { id: '123', content: { title: 'Demo' } } })

    render(<GenerateView apiKey="sk-test" onGenerated={onGenerated} />)

    await user.type(screen.getByPlaceholderText(/student's name/i), 'Rohail')
    await user.type(screen.getByPlaceholderText(/paste the assignment instructions/i), 'Write about growth strategy.')
    await user.click(screen.getByRole('button', { name: /generate professional assignment/i }))

    await waitFor(() =>
      expect(apiClient.post).toHaveBeenCalledWith(
        '/generate',
        expect.objectContaining({
          student_name: 'Rohail',
          additional_requirements: 'Write about growth strategy.',
          openai_api_key: 'sk-test',
        }),
        expect.any(Object),
      ),
    )
    expect(onGenerated).toHaveBeenCalled()
  })
})
