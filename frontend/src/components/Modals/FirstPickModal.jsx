import React, { useState } from 'react';

export default function FirstPickModal({ show, gameNum, time1, time2, onConfirm }) {
  const [sideEscolhido, setSideEscolhido] = useState(null);
  const [fpEscolhido, setFpEscolhido] = useState(null);

  if (!show) return null;

  // Assuming time1 is chooser in odd games, time2 in even games
  const chooser = gameNum % 2 !== 0 ? time1 : time2;
  const other = gameNum % 2 !== 0 ? time2 : time1;

  const valid = sideEscolhido && fpEscolhido;

  return (
    <div className="modal-overlay show" id="fpModal">
      <div className="modal-card" id="modalCard">
        <div className="modal-title" id="fpModalTitle">Jogo {gameNum} — vez do {chooser?.name} escolher</div>
        <div className="modal-sub" id="fpModalSub">Escolha o lado e quem começa o draft (first pick).</div>
        <div className="modal-choices" id="modalChoices">
          
          <div className="modal-group">
            <div className="modal-group-label">Lado</div>
            <div className="modal-choices-row" id="modalSideChoices">
              <button type="button" className={`modal-choice blue ${sideEscolhido === 'blue' ? 'chosen' : ''}`} onClick={() => setSideEscolhido('blue')}>Blue Side</button>
              <button type="button" className={`modal-choice red ${sideEscolhido === 'red' ? 'chosen' : ''}`} onClick={() => setSideEscolhido('red')}>Red Side</button>
            </div>
          </div>
          
          <div className="modal-group">
            <div className="modal-group-label">First Pick</div>
            <div className="modal-choices-row" id="modalFpChoices">
              <button type="button" className={`modal-choice ${fpEscolhido === 'chooser' ? 'chosen' : ''}`} onClick={() => setFpEscolhido('chooser')}>{chooser?.name}</button>
              <button type="button" className={`modal-choice ${fpEscolhido === 'other' ? 'chosen' : ''}`} onClick={() => setFpEscolhido('other')}>{other?.name}</button>
            </div>
          </div>
          
          <button type="button" className="modal-confirm-btn" id="modalConfirmBtn" disabled={!valid} onClick={() => onConfirm(sideEscolhido, fpEscolhido === 'chooser' ? true : false)}>
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
}
