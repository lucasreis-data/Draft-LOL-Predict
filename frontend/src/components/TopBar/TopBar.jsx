import React from 'react';

export default function TopBar({ liga, formato, onRestartDraft, onBackToConfig, phase, stepIndex }) {
  
  const phaseTabs = [
    {label:'Ban 1', range:[0,6], type:'ban'},
    {label:'Pick 1', range:[6,12], type:'pick'},
    {label:'Ban 2', range:[12,16], type:'ban'},
    {label:'Pick 2', range:[16,20], type:'pick'},
  ];

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="league-badge">🎮</div>
        <div className="league-text">
          <div className="league-picker" title="Liga definida na configuração da série">
            <span className="league-picker-label">Liga</span>
            <select className="league-select league-select-top" disabled value={liga}>
              <option value={liga}>{liga}</option>
            </select>
          </div>
          <span className="league-text sep">|</span>
          <span className="league-text fmt" id="fmtLabel">MD{formato}</span>
        </div>
      </div>

      <div className="phase-stepper" id="phaseStepper">
        {phaseTabs.map((p, i) => {
          const isActive = stepIndex >= p.range[0] && stepIndex < p.range[1];
          const isDone = stepIndex >= p.range[1];
          let cName = `phase-tab tab-${p.type}`;
          if (isActive) cName += ' active';
          if (isDone) cName += ' done';
          return (
            <div key={i} className={cName}>{p.label}</div>
          );
        })}
      </div>

      <div className="topbar-right">
        <div className="icon-btn" id="backToConfigBtn" title="Voltar à configuração da série" onClick={onBackToConfig}>⚔</div>
        <div className="icon-btn" id="settingsBtn" title="Reiniciar draft deste jogo" onClick={onRestartDraft}>↺</div>
      </div>
    </div>
  );
}
