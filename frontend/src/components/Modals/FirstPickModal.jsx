import React, { useState, useEffect } from 'react';

export default function FirstPickModal({ show, gameNum, time1, time2, onConfirm }) {
  const [sideEscolhido, setSideEscolhido] = useState(null);
  const [fpEscolhido, setFpEscolhido] = useState(null);

  useEffect(() => {
    if (show) {
      setSideEscolhido(null);
      setFpEscolhido(null);
    }
  }, [show]);

  if (!show) return null;
  const chooserIsTime1 = gameNum % 2 !== 0;
  const chooser = chooserIsTime1 ? time1 : time2;
  const other = chooserIsTime1 ? time2 : time1;

  const valid = sideEscolhido && fpEscolhido;

  const handleConfirm = () => {
    const chooserTemFP = fpEscolhido === 'chooser';
    const outroLado = (s) => (s === 'blue' ? 'red' : 'blue');

    const sideTime1 = chooserIsTime1 ? sideEscolhido : outroLado(sideEscolhido);
    const time1TemFP = chooserIsTime1 ? chooserTemFP : !chooserTemFP;

    onConfirm(sideTime1, time1TemFP);
  };
  

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
          
          <button type="button" className="modal-confirm-btn" id="modalConfirmBtn" disabled={!valid} onClick={handleConfirm}>
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
}
