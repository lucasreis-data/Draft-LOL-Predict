import React from 'react';
import { champImg } from '../../utils/riot';

export default function HistoryDrawer({ open, onClose, history }) {
  
  return (
    <>
      <div className={`drawer-panel ${open ? 'open' : ''}`} id="historicoPanel">
        <div className="suggest-head">
          <span className="t">Histórico da Série</span>
          <span className="x" id="closeHistorico" onClick={onClose}>✕</span>
        </div>
        <div className="suggest-body" id="historicoBody">
          {history.length === 0 ? (
            <p className="historico-empty">Nenhum jogo concluído ainda nesta série.</p>
          ) : (
            history.map((g, idx) => (
              <div key={idx} className="historico-jogo">
                <div className="historico-jogo-titulo">Jogo {g.jogo}</div>
                <div className="historico-time">
                  <span className="historico-time-nome">{g.fpName} (First Pick)</span>
                  <div className="historico-picks">
                    {g.picksFp.length ? g.picksFp.map(p => (
                      <span key={p} className="historico-pick-chip">
                        <img src={champImg(p)} alt="" loading="lazy" />{p}
                      </span>
                    )) : <span className="historico-vazio">—</span>}
                  </div>
                </div>
                <div className="historico-time">
                  <span className="historico-time-nome">{g.lpName} (Last Pick)</span>
                  <div className="historico-picks">
                    {g.picksLp.length ? g.picksLp.map(p => (
                      <span key={p} className="historico-pick-chip">
                        <img src={champImg(p)} alt="" loading="lazy" />{p}
                      </span>
                    )) : <span className="historico-vazio">—</span>}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
