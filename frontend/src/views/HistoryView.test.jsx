import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import HistoryView from './HistoryView'
import { apiClient } from '../lib/apiClient'

vi.mock('react-hot-toast', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}))

vi.mock('../lib/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    delete: vi.fn(),
  },
  getApiBaseUrl: () => 'http://localhost:8000',
  getErrorMessage: (_error, fallback) => fallback,
  isRecord: (value) => value !== null && typeof value === 'object' && !Array.isArray(value),
}))

describe('HistoryView', () => {
  it('loads history on mount', async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        history: [
          {
            id: 'h1',
            student_name: 'Rohail',
            course_code: 'MKT101',
            assignment_type: 'case_study',
            created_at: '2026-04-29T12:00:00.000Z',
          },
        ],
      },
    })

    render(<HistoryView setView={vi.fn()} onPrefill={vi.fn()} />)

    await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith('/history'))
    expect(await screen.findByText('Rohail')).toBeInTheDocument()
  })

  it('reuses assignment configuration', async () => {
    const user = userEvent.setup()
    const onPrefill = vi.fn()

    apiClient.get
      .mockResolvedValueOnce({
        data: {
          history: [
            {
              id: 'h1',
              student_name: 'Rohail',
              course_code: 'MKT101',
              assignment_type: 'case_study',
              created_at: '2026-04-29T12:00:00.000Z',
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          student_name: 'Rohail',
          course_code: 'MKT101',
          assignment_type: 'case_study',
          additional_requirements: 'Test',
          content: { assignment_number: '2', instructor: 'Prof X' },
        },
      })

    render(<HistoryView setView={vi.fn()} onPrefill={onPrefill} />)
    await screen.findByText('Rohail')
    await user.click(screen.getByRole('button', { name: /re-use/i }))

    await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith('/assignment/h1'))
    expect(onPrefill).toHaveBeenCalledWith(expect.objectContaining({ student_name: 'Rohail' }))
  })
})
