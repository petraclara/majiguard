import React, { useState, useEffect, useRef } from 'react';
import {
  Droplet,
  Send,
  RefreshCw,
  Search,
  X,
  AlertTriangle,
  Clock,
  MapPin,
  Shield,
  FileText
} from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000';

interface CaseDetails {
  case_id: string;
  created_at: string;
  original_report: string;
  redacted_report: string;
  follow_up_answers: string; // JSON string of dict
  issue_type: string;
  priority: string;
  affected_group: string | null;
  duration: string | null;
  location_hint: string | null;
  assessment_summary: string;
  immediate_guidance: string;
  recommended_actions: string;
  status: string;
}

interface Message {
  id: string;
  author: 'user' | 'agent' | 'system';
  text: string;
  timestamp: Date;
  caseDetails?: CaseDetails | null;
}

function App() {
  // Chat States
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userId] = useState(() => `usr-${Math.random().toString(36).substring(2, 9)}`);
  const [chatLoading, setChatLoading] = useState(false);

  // Dashboard States
  const [cases, setCases] = useState<CaseDetails[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseDetails | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [loadingCases, setLoadingCases] = useState(false);

  // System States
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Initial checks
  useEffect(() => {
    checkHealth();
    fetchCases();
  }, []);

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, chatLoading]);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        setApiConnected(true);
      } else {
        setApiConnected(false);
      }
    } catch {
      setApiConnected(false);
    }
  };

  const fetchCases = async () => {
    setLoadingCases(true);
    try {
      const res = await fetch(`${API_BASE}/api/cases`);
      if (res.ok) {
        const data = await res.json();
        setCases(data);
      }
    } catch (err) {
      console.error('Failed to fetch cases:', err);
    } finally {
      setLoadingCases(false);
    }
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputValue.trim() || chatLoading) return;

    const userText = inputValue.trim();
    setInputValue('');

    // Append user message
    const userMsg: Message = {
      id: Math.random().toString(),
      author: 'user',
      text: userText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setChatLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          message: userText
        })
      });

      if (!res.ok) {
        throw new Error('Server returned an error');
      }

      const data = await res.json();
      
      // Update session ID if it was generated
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Append agent response
      const agentMsg: Message = {
        id: Math.random().toString(),
        author: 'agent',
        text: data.response,
        timestamp: new Date(),
        caseDetails: data.case_details
      };
      setMessages(prev => [...prev, agentMsg]);

      // If it's the final triage, reset session ID and refresh cases
      if (data.is_final) {
        setSessionId(null);
        fetchCases();
        if (data.case_details) {
          setSelectedCase(data.case_details);
        }
      }
    } catch (err) {
      console.error(err);
      const systemMsg: Message = {
        id: Math.random().toString(),
        author: 'system',
        text: 'Connection error: Unable to contact the MajiGuard Agent. Please check if the server is running.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, systemMsg]);
    } finally {
      setChatLoading(false);
    }
  };

  const loadDemoScenarios = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/demo/load`, { method: 'POST' });
      if (res.ok) {
        alert('Demo scenarios loaded successfully!');
        fetchCases();
      }
    } catch (err) {
      console.error(err);
      alert('Failed to load demo scenarios.');
    }
  };

  const handleUpdateStatus = async (caseId: string, newStatus: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/cases/${caseId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        fetchCases();
        // Update selected case in-place
        if (selectedCase && selectedCase.case_id === caseId) {
          setSelectedCase({ ...selectedCase, status: newStatus });
        }
      }
    } catch (err) {
      console.error('Failed to update case status:', err);
    }
  };

  const loadQuickStart = (text: string) => {
    setInputValue(text);
  };

  // Filters calculation
  const filteredCases = cases.filter(c => {
    const matchesPriority = priorityFilter ? c.priority === priorityFilter : true;
    const matchesType = typeFilter ? c.issue_type === typeFilter : true;
    const matchesSearch = searchQuery
      ? c.original_report.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (c.location_hint && c.location_hint.toLowerCase().includes(searchQuery.toLowerCase()))
      : true;
    return matchesPriority && matchesType && matchesSearch;
  });

  const getPriorityClass = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'priority-critical';
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return 'type-label';
    }
  };

  const getStatusClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'new': return 'status-new';
      case 'reviewing': return 'status-reviewing';
      case 'assigned': return 'status-assigned';
      case 'resolved': return 'status-resolved';
      default: return 'type-label';
    }
  };

  const formatIssueType = (type: string) => {
    return type
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  };

  const renderTriageCard = (details: CaseDetails) => {
    return (
      <div className="triage-card">
        <h3>
          <Shield size={20} />
          MajiGuard Triage Summary
        </h3>
        <div className="triage-grid">
          <div className="triage-item">
            <span className="triage-label">Case ID</span>
            <span className="triage-val" style={{ fontFamily: 'monospace' }}>{details.case_id}</span>
          </div>
          <div className="triage-item">
            <span className="triage-label">Priority</span>
            <span className={`badge ${getPriorityClass(details.priority)}`}>{details.priority}</span>
          </div>
          <div className="triage-item">
            <span className="triage-label">Issue Type</span>
            <span className="triage-val">{formatIssueType(details.issue_type)}</span>
          </div>
          <div className="triage-item">
            <span className="triage-label">Reported Duration</span>
            <span className="triage-val">{details.duration || 'Not specified'}</span>
          </div>
        </div>
        <div>
          <div className="triage-section-title">Immediate Safety Guidance</div>
          <div className="content-block guidance" style={{ fontSize: '0.85rem', margin: 0, padding: '0.75rem' }}>
            {details.immediate_guidance}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo">
            <Droplet />
          </div>
          <div className="app-title-group">
            <h1>MajiGuard</h1>
            <p>AI-Powered Community Water Triage System • Capstone MVP</p>
          </div>
        </div>
        
        <div className="header-actions">
          <button className="btn-demo" onClick={loadDemoScenarios}>
            <Clock size={16} />
            Load Demo Scenarios
          </button>
          <div className="api-status" onClick={checkHealth} style={{ cursor: 'pointer' }}>
            <span className={`status-dot ${apiConnected === null ? 'loading' : apiConnected ? '' : 'error'}`} />
            {apiConnected === null ? 'Connecting...' : apiConnected ? 'Connected' : 'Offline (Retry)'}
          </div>
        </div>
      </header>

      {/* Main split layout */}
      <div className="app-workspace">
        
        {/* Left: Chat Panel */}
        <section className="chat-panel">
          <div className="chat-history">
            {messages.length === 0 ? (
              <div className="chat-welcome">
                <div className="welcome-icon">
                  <Droplet size={48} />
                </div>
                <h2>Water Support intake</h2>
                <p>
                  Submit a water contamination, shortage, or infrastructure issue in plain language.
                  Our coordinator agent will verify details and route your case.
                </p>
                <div className="quick-starts">
                  <button 
                    className="quick-start-card"
                    onClick={() => loadQuickStart("The tap water near our elementary school is very brown since yesterday morning and children are drinking from it.")}
                  >
                    <span className="quick-start-icon"><AlertTriangle size={18} /></span>
                    <span className="quick-start-text">Brown water near school, children affected</span>
                  </button>
                  <button 
                    className="quick-start-card"
                    onClick={() => loadQuickStart("The main borehole in our village has stopped working completely. People are queuing since 4 AM.")}
                  >
                    <span className="quick-start-icon"><RefreshCw size={18} /></span>
                    <span className="quick-start-text">Broken borehole pump, long queues</span>
                  </button>
                </div>
              </div>
            ) : (
              messages.map(msg => (
                <div key={msg.id} className={`message-bubble ${msg.author}`}>
                  <span className="message-author">{msg.author}</span>
                  <div>{msg.text}</div>
                  {msg.caseDetails && renderTriageCard(msg.caseDetails)}
                </div>
              ))
            )}
            
            {chatLoading && (
              <div className="message-bubble agent">
                <span className="message-author">agent</span>
                <div className="typing-indicator">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="chat-input-area">
            <div className="chat-privacy-notice">
              <Shield size={12} />
              <span>Privacy notice: PII is redacted. Do not submit national IDs or bank secrets.</span>
            </div>
            <form onSubmit={handleSendMessage} className="chat-input-form">
              <input
                type="text"
                className="chat-input"
                placeholder="Describe the water issue..."
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                disabled={chatLoading}
              />
              <button type="submit" className="btn-send" disabled={!inputValue.trim() || chatLoading}>
                <Send size={18} />
              </button>
            </form>
          </div>
        </section>

        {/* Right: Dashboard Panel */}
        <section className="dashboard-panel">
          <div className="dashboard-header">
            <div className="dashboard-controls">
              <div className="dashboard-title-group">
                <h2>Triage Cases</h2>
                <p>Support team dashboard for case management and review</p>
              </div>
              <button className="btn-demo" onClick={fetchCases} title="Refresh Cases">
                <RefreshCw size={16} />
              </button>
            </div>
            <div className="dashboard-controls">
              <div className="search-wrapper">
                <Search className="search-icon" size={16} />
                <input
                  type="text"
                  className="search-input"
                  placeholder="Search cases..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="filter-group">
                <select
                  className="select-filter"
                  value={priorityFilter}
                  onChange={e => setPriorityFilter(e.target.value)}
                >
                  <option value="">All Priorities</option>
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
                <select
                  className="select-filter"
                  value={typeFilter}
                  onChange={e => setTypeFilter(e.target.value)}
                >
                  <option value="">All Types</option>
                  <option value="possible_contamination">Contamination</option>
                  <option value="infrastructure_failure">Infrastructure</option>
                  <option value="water_shortage">Shortage</option>
                  <option value="long_queue_or_access_issue">Access/Queues</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <div className="cases-grid">
            {loadingCases ? (
              <div className="cases-empty">
                <RefreshCw size={36} className="loading" style={{ animation: 'pulse 1.5s infinite' }} />
                <p>Loading cases...</p>
              </div>
            ) : filteredCases.length === 0 ? (
              <div className="cases-empty">
                <FileText />
                <h3>No Cases Found</h3>
                <p>No triage cases match the selected filters or search terms.</p>
              </div>
            ) : (
              filteredCases.map(c => (
                <div
                  key={c.case_id}
                  className={`case-card ${selectedCase?.case_id === c.case_id ? 'active' : ''}`}
                  onClick={() => setSelectedCase(c)}
                >
                  <div className="case-card-header">
                    <span className="case-id">{c.case_id}</span>
                    <span className="case-date">{new Date(c.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="case-card-body">
                    <h3>{c.original_report}</h3>
                  </div>
                  <div className="case-badge-row">
                    <span className={`badge ${getPriorityClass(c.priority)}`}>{c.priority}</span>
                    <span className={`badge ${getStatusClass(c.status)}`}>{c.status}</span>
                    <span className="badge type-label">{formatIssueType(c.issue_type)}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Case Details Drawer overlay */}
      {selectedCase && (
        <div className="case-details-drawer">
          <div className="drawer-header">
            <div className="drawer-title-group">
              <h3>Case Details</h3>
              <span className="case-id" style={{ fontSize: '0.875rem' }}>{selectedCase.case_id}</span>
            </div>
            <button className="btn-close" onClick={() => setSelectedCase(null)}>
              <X size={20} />
            </button>
          </div>

          <div className="drawer-content">
            <div className="status-manager">
              <span className="meta-label">Manage Status</span>
              <select
                value={selectedCase.status}
                onChange={e => handleUpdateStatus(selectedCase.case_id, e.target.value)}
              >
                <option value="new">New</option>
                <option value="reviewing">Reviewing</option>
                <option value="assigned">Assigned</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>

            <div className="drawer-meta-grid">
              <div className="meta-item">
                <span className="meta-label">Issue Type</span>
                <span className="meta-value">{formatIssueType(selectedCase.issue_type)}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Priority</span>
                <span className={`badge ${getPriorityClass(selectedCase.priority)}`} style={{ width: 'fit-content' }}>
                  {selectedCase.priority}
                </span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Affected Group</span>
                <span className="meta-value">{selectedCase.affected_group || 'Not specified'}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Reported Duration</span>
                <span className="meta-value">{selectedCase.duration || 'Not specified'}</span>
              </div>
              <div className="meta-item" style={{ gridColumn: 'span 2' }}>
                <span className="meta-label">Location Hint</span>
                <span className="meta-value">
                  <MapPin size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
                  {selectedCase.location_hint || 'Not specified'}
                </span>
              </div>
            </div>

            <div className="drawer-section">
              <h4>Sanitized Report (PII Redacted)</h4>
              <div className="content-block redacted">
                {selectedCase.redacted_report}
              </div>
            </div>

            <div className="drawer-section">
              <h4>Assessment Summary</h4>
              <div className="content-block">
                {selectedCase.assessment_summary}
              </div>
            </div>

            <div className="drawer-section">
              <h4>Immediate Safety Guidance</h4>
              <div className="content-block guidance">
                {selectedCase.immediate_guidance}
              </div>
            </div>

            <div className="drawer-section">
              <h4>Recommended Next Steps</h4>
              <div className="content-block actions">
                {selectedCase.recommended_actions}
              </div>
            </div>
            
            {/* Show follow-up Q&A if present */}
            {selectedCase.follow_up_answers && (
              <div className="drawer-section">
                <h4>Clarification Q&A</h4>
                <div className="content-block qa-list" style={{ backgroundColor: 'var(--bg-primary)' }}>
                  {(() => {
                    try {
                      const answers = JSON.parse(selectedCase.follow_up_answers);
                      const keys = Object.keys(answers);
                      if (keys.length === 0) return <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>No follow-up questions were required.</p>;
                      return keys.map((key, i) => (
                        <div key={key} className="qa-item">
                          <span className="qa-question">Clarification Question #{i+1}</span>
                          <span className="qa-answer">{answers[key]}</span>
                        </div>
                      ));
                    } catch {
                      return <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>No follow-up questions were required.</p>;
                    }
                  })()}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
