import React from 'react';

export default function BottomBar({ nextGameAction, isDraftFinished, gameCur, gameTot, isSeriesFinished, suggestionsOn, onToggleSuggestions }) {
  
  return (
    <div className="bottombar">
      <div className="bottombar-inner">
        <div className="bb-left">
          <div className="drafter">
            <div className="av">🧠</div>
            <div>
              <div className="name">Drafter</div>
              <div className="status"><span className="dot"></span>Sistema pronto</div>
            </div>
          </div>

          <div className="bb-actions">
            <div 
              className={`bb-btn ${isDraftFinished && !isSeriesFinished ? 'pulse-accent' : 'disabled-btn'}`} 
              id="nextGameBtn"
              onClick={isDraftFinished && !isSeriesFinished ? nextGameAction : undefined}
            >
              {isSeriesFinished ? 'Série Finalizada' : 'Próximo Jogo ▶'}
            </div>
          </div>
        </div>

        <div className="bb-center">
          <span className="series-label">Jogo: <span id="gameCur">{gameCur}</span>/<span id="gameTot">{gameTot}</span></span>
          <div className="series-dots" id="seriesDots">
            {Array.from({length: gameTot}).map((_, i) => (
              <span key={i} className={i < gameCur - 1 ? 'done' : (i === gameCur - 1 ? 'current' : '')}></span>
            ))}
          </div>
        </div>

        <div className="bb-right">
          <span className="switch-label">Destacar sugestões no grid</span>
          <div className={`switch ${suggestionsOn ? 'on' : ''}`} id="togglePickSuggest" onClick={onToggleSuggestions}></div>
        </div>
      </div>
    </div>
  );
}
