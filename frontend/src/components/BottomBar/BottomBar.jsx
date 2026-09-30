import React from 'react';

export default function BottomBar({ onOpenHistory }) {
  
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
        </div>

        <div className="bb-center">
          {/* Removido para a center-info-bar superior */}
        </div>

        <div className="bb-right">
          <div className="bb-btn" onClick={onOpenHistory}>
            📊 Histórico da Série
          </div>
        </div>
      </div>
    </div>
  );
}
