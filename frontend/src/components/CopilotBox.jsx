import { useEffect, useState } from 'react';
import { useCopilot } from '../hooks/useRouters';
import { formatFixType } from '../utils/formatters';

const SUGGESTED_QUESTIONS = [
  'Why is this router performing badly?',
  'Is this router healthy?',
];

export default function CopilotBox({ routerId }) {
  const [questionText, setQuestionText] = useState('');
  const { answer, loading, error, askQuestion, resetAnswer } = useCopilot();

  useEffect(() => {
    resetAnswer();
    setQuestionText('');
  }, [routerId, resetAnswer]);

  const submitQuestion = async (finalQuestion) => {
    const trimmed = String(finalQuestion || '').trim();
    if (!trimmed) return;

    const scopedQuestion = `${trimmed} for router ${routerId}`;
    await askQuestion(scopedQuestion);
  };

  const handleSubmit = async () => {
    await submitQuestion(questionText);
  };

  const handleChipClick = async (chipText) => {
    setQuestionText(chipText);
    await submitQuestion(chipText);
  };

  return (
    <div className="copilot-box">
      <div className="copilot-header">
        <h3>Copilot insight</h3>
      </div>

      <div className="chip-row">
        {SUGGESTED_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            className="chip"
            onClick={() => handleChipClick(question)}
            disabled={loading}
          >
            {question}
          </button>
        ))}
      </div>

      <div className="copilot-input-row">
        <input
          type="text"
          value={questionText}
          onChange={(event) => setQuestionText(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              handleSubmit();
            }
          }}
          placeholder="Ask why this router is performing badly"
          disabled={loading}
        />

        <button type="button" className="primary-button" onClick={handleSubmit} disabled={loading || !questionText.trim()}>
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </div>

      {loading && (
        <div className="state-box neutral-box">
          <p>Thinking...</p>
        </div>
      )}

      {error && (
        <div className="state-box error-box">
          <p>Couldn't get an answer. Try again.</p>
          <button type="button" className="secondary-button" onClick={() => submitQuestion(questionText)}>
            Retry
          </button>
        </div>
      )}

      {answer && (
        <div className="answer-box">
          <div className="answer-row">
            <span className="answer-label">Cause</span>
            <p>{answer.cause}</p>
          </div>
          <div className="answer-row">
            <span className="answer-label">Evidence</span>
            <p>{answer.evidence}</p>
          </div>
          <div className="answer-row">
            <span className="answer-label">Recommended fix</span>
            <p>{formatFixType(answer.recommended_fix)}</p>
          </div>
        </div>
      )}
    </div>
  );
}
