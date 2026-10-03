import { useEffect, useState } from 'react';

const API_URL = 'https://esports-api.lolesports.com/persisted/gw/getTeams?hl=en-US';
const API_KEY = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z';

let cache = null;      
let pending = null;

const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
const strip = (s) => norm(s).replace(/(esports|gaming|team|club)$/g, '');

function load() {
  if (cache) return Promise.resolve(cache);
  if (!pending) {
    pending = fetch(API_URL, { headers: { 'x-api-key': API_KEY } })
      .then((r) => r.json())
      .then((json) => {
        const byName = new Map();
        const byCode = new Map();
        (json?.data?.teams || []).forEach((t) => {
          if (!t.image) return;
          byName.set(norm(t.name), t.image);
          byName.set(strip(t.name), t.image);
          if (t.code) byCode.set(norm(t.code), t.image);
        });
        cache = { byName, byCode };
        return cache;
      })
      .catch((e) => {
        console.error('Falha ao carregar logos dos times', e);
        pending = null;
        return { byName: new Map(), byCode: new Map() };
      });
  }
  return pending;
}

function findLogo(data, name) {
  if (!data || !name) return null;
  return data.byName.get(norm(name)) || data.byName.get(strip(name)) || data.byCode.get(norm(name)) || null;
}

export function useTeamLogo(name) {
  const [logo, setLogo] = useState(() => findLogo(cache, name));
  useEffect(() => {
    let alive = true;
    load().then((data) => { if (alive) setLogo(findLogo(data, name)); });
    return () => { alive = false; };
  }, [name]);
  return logo;
}