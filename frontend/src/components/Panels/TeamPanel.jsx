import React from 'react';
import { champImg, champSplash, initials, PALETTE, hashStr } from '../../utils/riot';

const PICK_SLOTS = [1, 2, 3, 4, 5];
export default function TeamPanel({ side, team, picks, bans, isTurn }) {
  if (!team) return null;

  const isBlue = side === 'blue';
  const turnClass = isTurn ? (isBlue ? 'is-turn-active is-blue-side' : 'is-turn-active is-red-side') : '';
  
  const renderRoster = () => {
  return PICK_SLOTS.map((n, i) => {
    const champ = picks[i];
    const isFilled = !!champ;

    return (
      <div key={n} className={`role-row ${isFilled ? 'filled' : ''}`}>
        {isFilled && <img className="row-bg" alt="" loading="lazy" src={champSplash(champ)} />}
        <div className="role-icon">{n}</div>
        <div className="role-info">
          <div className="role-label">Pick {n}</div>
          <div className="player-name">{isFilled ? champ : '—'}</div>
        </div>
      </div>
    );
  });
};

  const renderBans = () => {
    const slots = [];
    for(let i=0; i<5; i++){
      const champ = bans[i];
      if (champ) {
        slots.push(
          <div key={`ban-${i}`} className="ban-slot filled" style={{background: PALETTE[hashStr(champ) % PALETTE.length]}}>
            <span className="slot-fallback">{initials(champ)}</span>
            <img className="slot-img" src={champImg(champ)} alt="" loading="lazy" />
          </div>
        );
      } else {
        slots.push(<div key={`ban-${i}`} className="ban-slot"></div>);
      }
    }
    return slots;
  };

  const renderBadge = () => {
    if (team.logo) {
      return <img className="team-logo-img" src={team.logo} alt={team.name} />;
    }
    return <span className="badge-fallback">{team.name.substring(0,3).toUpperCase()}</span>;
  };

  return (
    <div className={`side ${side} ${turnClass}`} id={isBlue ? 'sideBlue' : 'sideRed'}>
      <div className="side-head">
        {isBlue && (
          <div className="team-badge" id="teamBadgeBlue">
            {renderBadge()}
          </div>
        )}
        {!isBlue && (
          <div className={`turn-flag ${isTurn ? 'active' : ''}`}>▶</div>
        )}
        
        <div className="meta">
          <div className="team-name">{team.name}</div>
          <div className="label side-tag">{isBlue ? 'Blue Side' : 'Red Side'}</div>
        </div>
        
        {isBlue && (
          <div className={`turn-flag ${isTurn ? 'active' : ''}`}>▶</div>
        )}
        {!isBlue && (
          <div className="team-badge" id="teamBadgeRed">
            {renderBadge()}
          </div>
        )}
      </div>

      <div className="roster">
        {renderRoster()}
      </div>

      <div className="bans-block">
        <div className="bans-head">
          {isBlue ? (
            <><span>‹ Bans</span><span>{bans.length}/5</span></>
          ) : (
            <><span>{bans.length}/5</span><span>Bans ›</span></>
          )}
        </div>
        <div className="bans-row">
          {renderBans()}
        </div>
      </div>
    </div>
  );
}
