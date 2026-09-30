import React from 'react';

export default function EndSeriesModal({ show, onHistory, onRestart }) {
  if (!show) return null;

  return (
    <div className="modal-overlay show" id="fpModal">
      <div className="modal-card" id="modalCard">
        <div className="modal-title" id="fpModalTitle">Série Finalizada</div>
        <div className="modal-sub" id="fpModalSub">A série foi concluída.</div>
        <div className="modal-choices" id="modalChoices">
          <button type="button" className="modal-confirm-btn secondary" id="btnVerHistorico" style={{marginBottom: '10px'}} onClick={onHistory}>
            📊 Ver Histórico da Série
          </button>
          <button type="button" className="modal-confirm-btn" id="btnNovoDraft" onClick={onRestart}>
            🔄 Iniciar Novo Draft
          </button>
        </div>
      </div>
    </div>
  );
}
