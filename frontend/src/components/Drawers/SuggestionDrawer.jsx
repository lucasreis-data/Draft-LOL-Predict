import React from 'react';
import { champImg } from '../../utils/riot';

export default function SuggestionDrawer({ open, onClose, suggestions, isPlayerTurn, playerTeamName }) {
  
  const campeoes = suggestions.campeoes || [];
  
  let content = null;
  if (campeoes.length === 0) {
    content = <div className="historico-empty">Sem sugestão da IA no momento (draft ainda não começou, encerrado, ou a API Python está fora do ar).</div>;
  } else if (!isPlayerTurn) {
    content = <div className="historico-empty">Sugestão disponível só pro {playerTeamName} (Time 1). Na vez do adversário, use o botão "IA joga".</div>;
  } else {
    const titulo = (suggestions.tipo === 'ban' ? 'Sugestão de Ban' : 'Sugestões de Pick (ordem da IA)') + ` — ${playerTeamName}`;
    content = (
      <div className="historico-jogo">
        <div className="historico-jogo-titulo">{titulo}</div>
        {campeoes.map((nome, i) => (
          <div key={nome} className="historico-time" style={{display:'flex', alignItems:'center', gap:'10px'}}>
            <span className="score-champ total" style={{fontFamily:"'Rajdhani',sans-serif"}}>#{i+1}</span>
            <div className="score-champ" style={{fontSize:'13px'}}>
              <img src={champImg(nome)} alt="" loading="lazy" />
              {nome}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <>
      <div className={`drawer-panel ${open ? 'open' : ''}`} id="suggestPanel">
        <div className="suggest-head">
          <span className="t">Ranking Score</span>
          <span className="x" id="closeSuggest" onClick={onClose}>✕</span>
        </div>
        <div className="suggest-body" id="suggestBodyWrap">
          {content}
        </div>
      </div>
      <div className={`drawer-tab ${open ? 'panel-open' : ''}`} id="iaTab" title="Abrir/fechar recomendações da IA" onClick={onClose}>
        {open ? 'IA ›' : '‹ IA'}
      </div>
    </>
  );
}
