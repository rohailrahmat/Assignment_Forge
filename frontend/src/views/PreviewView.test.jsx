import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PreviewView from './PreviewView'
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
    post: vi.fn(),
  },
  getApiBaseUrl: () => 'http://localhost:8000',
  getErrorMessage: (_error, fallback) => fallback,
  isRecord: (value) => value !== null && typeof value === 'object' && !Array.isArray(value),
}))

describe('PreviewView', () => {
  it('shows empty state when generated content is missing', async () => {
    const user = userEvent.setup()
    const setView = vi.fn()

    render(<PreviewView generated={null} setView={setView} />)

    await user.click(screen.getByRole('button', { name: /generate assignment/i }))
    expect(setView).toHaveBeenCalledWith('generate')
  })

  it('downloads docx for generated assignment', async () => {
    const user = userEvent.setup()
    const createObjectUrlSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock')
    const revokeObjectUrlSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    apiClient.get.mockResolvedValueOnce({ data: new Blob(['doc']) })

    render(
      <PreviewView
        setView={vi.fn()}
        generated={{
          id: 'a1',
          content: {
            title: 'Assignment',
            student_name: 'Rohail',
            course: 'MKT101',
            assignment_number: '1',
            sections: [],
          },
        }}
      />,
    )

    await user.click(screen.getAllByRole('button', { name: /word/i })[0])

    await waitFor(() =>
      expect(apiClient.get).toHaveBeenCalledWith(
        'http://localhost:8000/download/docx/a1',
        expect.objectContaining({ responseType: 'blob' }),
      ),
    )

    createObjectUrlSpy.mockRestore()
    revokeObjectUrlSpy.mockRestore()
  })
})
