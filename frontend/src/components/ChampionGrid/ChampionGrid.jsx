import React from 'react';
import { champImg, fuzzyMatch, PALETTE, hashStr } from '../../utils/riot';

export default function ChampionGrid({ 
  champions, 
  searchQuery, 
  bannedList, 
  pendingChampion, 
  setPendingChampion, 
  suggestions, 
  suggestionsOn, 
  isTurnForPlayer 
}) {

  const top3 = (suggestionsOn && isTurnForPlayer) ? suggestions.campeoes : [];
  const ehSugestaoDeBan = suggestionsOn && suggestions.tipo === 'ban';

  const filtered = champions.filter(c => fuzzyMatch(searchQuery, c.name));

  return (
    <div className="champ-grid" id="champGrid">
      {filtered.map(c => {
        const name = c.name;
        const isBanned = bannedList.includes(name);
        const isSelected = pendingChampion === name;
        const rank = top3.indexOf(name);
        
        let cName = 'champ-card';
        if (isBanned) cName += ' disabled';
        if (isSelected) cName += ' selected';
        
        let rankData = null;
        if (rank > -1) {
          cName += ` suggested nivel-${rank+1}`;
          rankData = rank + 1;
          if (ehSugestaoDeBan) cName += ' fase-ban';
        }

        return (
          <div 
            key={name} 
            className={cName} 
            data-champ={name}
            data-rank={rankData}
            onClick={() => {
              if (!isBanned) {
                setPendingChampion(prev => prev === name ? null : name);
              }
            }}
          >
            <div className="portrait" style={{background: PALETTE[hashStr(name)%PALETTE.length]}}></div>
            <img className="portrait-img" src={champImg(name)} alt="" loading="lazy" />
            <div className="name">{name}</div>
          </div>
        );
      })}
    </div>
  );
}
