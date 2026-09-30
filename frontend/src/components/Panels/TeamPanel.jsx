import React from 'react';
import { champImg, champSplash, initials, PALETTE, hashStr } from '../../utils/riot';

const ROLES = [
  {id:'top', label:'Top', color:'var(--r-top)'},
  {id:'jng', label:'Jng', color:'var(--r-jng)'},
  {id:'mid', label:'Mid', color:'var(--r-mid)'},
  {id:'adc', label:'Adc', color:'var(--r-adc)'},
  {id:'sup', label:'Support', color:'var(--r-sup)'},
];
const roleIcon = {top:'⚔', jng:'✳', mid:'✦', adc:'✛', sup:'✚'};
const roleColorVar = {top:'--r-top', jng:'--r-jng', mid:'--r-mid', adc:'--r-adc', sup:'--r-sup'};

export default function TeamPanel({ side, team, picks, bans, isTurn }) {
  if (!team) return null;

  const isBlue = side === 'blue';
  const turnClass = isTurn ? (isBlue ? 'is-turn-active is-blue-side' : 'is-turn-active is-red-side') : '';
  
  const renderRoster = () => {
    return ROLES.map((r, i) => {
      const champ = picks[i];
      const role = r.id;
      const isFilled = !!champ;

      return (
        <div key={role} className={`role-row ${isFilled ? 'filled' : ''}`}>
          {isFilled && <img className="row-bg" alt="" loading="lazy" src={champSplash(champ)} />}
          <div className="role-icon" style={{background: `var(${roleColorVar[role]})`}}>{roleIcon[role]}</div>
          <div className="role-info">
            <div className="role-label">{r.label}</div>
            <div className="player-name">Jogador {i+1}</div>
          </div>
          {isFilled ? (
            <div className="champ-slot" style={{background: PALETTE[hashStr(champ) % PALETTE.length]}}>
              <span className="slot-fallback">{initials(champ)}</span>
              <img className="slot-img" src={champImg(champ)} alt="" loading="lazy" />
            </div>
          ) : (
            <div className="champ-slot">—</div>
          )}
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
