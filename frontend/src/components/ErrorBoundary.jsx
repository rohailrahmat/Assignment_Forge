import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error) {
    console.error('Unhandled UI error:', error)
  }

  handleReset = () => {
    this.setState({ hasError: false })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="page">
          <div className="card">
            <div className="card-header">
              <div className="card-icon gold">!</div>
              <div>
                <div className="card-title">Something went wrong</div>
                <div className="card-desc">Please reload the page and try again.</div>
              </div>
            </div>
            <div className="card-body">
              <button className="btn btn-primary" onClick={this.handleReset}>
                Retry
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
