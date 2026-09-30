import React, { useEffect, useState } from 'react';
import { draftService } from '../../service/DraftService';

export default function ConfigModal({ show, ligas, onConfirm }) {
  const [ligaEscolhida, setLigaEscolhida] = useState('');
  const [times, setTimes] = useState([]);
  const [time1, setTime1] = useState('');
  const [time2, setTime2] = useState('');
  const [formato, setFormato] = useState(5);

  useEffect(() => {
    if (ligaEscolhida) {
      draftService.getTimes(ligaEscolhida).then(res => setTimes(res.map(name => ({ key: name, name, short: name.slice(0,3).toUpperCase() }))));
    }
  }, [ligaEscolhida]);

  if (!show) return null;

  const valid = ligaEscolhida && time1 && time2 && time1 !== time2 && formato;

  return (
    <div className="modal-overlay show" id="fpModal">
      <div className="modal-card modal-card-wide" id="modalCard">
        <div className="modal-title" id="fpModalTitle">Configurar Série</div>
        <div className="modal-sub" id="fpModalSub"></div>
        <div className="modal-choices" id="modalChoices">
          
          <div className="modal-group">
            <div className="modal-group-label">Liga</div>
            <div className="modal-choices-row" id="modalLigaChoices">
              {ligas.length === 0 ? <span style={{fontSize:'12px', color:'var(--text-faint)'}}>Carregando ligas...</span> : 
                ligas.map(l => (
                  <button key={l} type="button" className={`modal-choice ${ligaEscolhida === l ? 'chosen' : ''}`} onClick={() => setLigaEscolhida(l)}>{l}</button>
                ))
              }
            </div>
          </div>

          <div className="team-picker-row">
            <div className={`team-picker-card ${time1 ? 'chosen' : ''}`} id="teamCard1">
              <div className="team-picker-label">TIME 1</div>
              <div className="team-picker-avatar" id="teamAvatar1">
                <span className="tp-avatar-fallback">{times.find(t => t.key === time1)?.short || '?'}</span>
              </div>
              <div className="team-picker-status" id="teamStatus1">{time1 ? times.find(t => t.key === time1)?.name : 'Nenhum time selecionado'}</div>
              <select className="modal-select" id="modalTime1" disabled={!ligaEscolhida} value={time1} onChange={e => setTime1(e.target.value)}>
                <option value="">{ligaEscolhida ? 'Selecione...' : 'Escolha a liga primeiro'}</option>
                {times.map(t => <option key={t.key} value={t.key}>{t.name}</option>)}
              </select>
            </div>
            
            <div className="team-picker-vs">⚔</div>
            
            <div className={`team-picker-card ${time2 ? 'chosen' : ''}`} id="teamCard2">
              <div className="team-picker-label">TIME 2</div>
              <div className="team-picker-avatar" id="teamAvatar2">
                <span className="tp-avatar-fallback">{times.find(t => t.key === time2)?.short || '?'}</span>
              </div>
              <div className="team-picker-status" id="teamStatus2">{time2 ? times.find(t => t.key === time2)?.name : 'Nenhum time selecionado'}</div>
              <select className="modal-select" id="modalTime2" disabled={!ligaEscolhida} value={time2} onChange={e => setTime2(e.target.value)}>
                <option value="">{ligaEscolhida ? 'Selecione...' : 'Escolha a liga primeiro'}</option>
                {times.map(t => <option key={t.key} value={t.key}>{t.name}</option>)}
              </select>
            </div>
          </div>

          <div className="modal-group">
            <div className="modal-group-label">Formato da Série</div>
            <div className="modal-choices-row" id="modalFormatoChoices">
              {[1,3,5].map(f => (
                <button key={f} type="button" className={`modal-choice ${formato === f ? 'chosen' : ''}`} onClick={() => setFormato(f)}>MD{f}</button>
              ))}
            </div>
          </div>

          <button type="button" className="modal-confirm-btn" id="modalConfirmBtn" disabled={!valid} onClick={() => onConfirm(times.find(t=>t.key===time1), times.find(t=>t.key===time2), formato, ligaEscolhida)}>
            ⚡ Iniciar Draft
          </button>
        </div>
      </div>
    </div>
  );
}
