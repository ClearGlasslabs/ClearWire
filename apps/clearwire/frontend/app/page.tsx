'use client';

import { useMemo, useState } from 'react';
import { Activity, Antenna, Bell, Bluetooth, Database, FileText, Gauge, LockKeyhole, Map, Radio, ScanLine, Settings, ShieldCheck, Wifi, WifiOff } from 'lucide-react';

type Obs={id:string;tech:string;label:string;signal:number;risk:number;channel?:number};
const obs:Obs[]=[
 {id:'7f2a91c4',tech:'Wi-Fi',label:'Authorized AP',signal:-48,risk:18,channel:36},
 {id:'a12bc773',tech:'Wi-Fi',label:'Lab AP',signal:-67,risk:31,channel:149},
 {id:'5e09c2a1',tech:'BLE',label:'Temperature Sensor',signal:-61,risk:14},
 {id:'3b88d021',tech:'BLE',label:'Asset Beacon',signal:-78,risk:42},
 {id:'c40f98be',tech:'IoT',label:'Authorized IoT',signal:-58,risk:55,channel:6},
];
const nav=[['Overview',Gauge],['Live Map',Map],['Devices',Radio],['Signals',Activity],['Wireless Assets',Antenna],['Exposure Audit',ShieldCheck],['Reports',FileText],['Integrations',Database],['Audit Log',LockKeyhole],['Settings',Settings]] as const;

export default function Home(){
 const [page,setPage]=useState('Overview');
 const [authorized,setAuthorized]=useState(false);
 const [privacy,setPrivacy]=useState(true);
 const high=useMemo(()=>obs.filter(x=>x.risk>=50).length,[ ]);
 return <main className="min-h-screen grid-bg">
  <header className="sticky top-0 z-20 border-b border-cyan-400/15 bg-slate-950/90 backdrop-blur-xl px-5 py-3 flex items-center justify-between">
   <div className="flex items-center gap-3"><div className="h-9 w-9 rounded-xl bg-cyan-300/10 border border-cyan-300/30 grid place-items-center glow"><Radio size={19}/></div><div><div className="font-semibold tracking-[.18em]">CLEARWIRE</div><div className="text-[10px] text-cyan-200/55 uppercase tracking-[.2em]">Wireless Intelligence</div></div></div>
   <div className="hidden md:flex items-center gap-5 text-xs text-slate-300"><span>Workspace: <b className="text-cyan-200">Authorized Lab</b></span><span className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-cyan-300 animate-pulse"/>Sensor simulator online</span><Bell size={17}/></div>
  </header>
  <div className="flex">
   <aside className="hidden lg:block w-60 border-r border-cyan-400/10 min-h-[calc(100vh-61px)] p-3">
    <div className="text-[10px] text-slate-500 uppercase tracking-[.2em] px-3 py-3">Operations</div>
    {nav.map(([label,Icon])=><button key={label} onClick={()=>setPage(label)} className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm mb-1 text-left ${page===label?'bg-cyan-300/10 text-cyan-200 border border-cyan-300/15':'text-slate-400 hover:text-white hover:bg-white/5'}`}><Icon size={16}/>{label}</button>)}
   </aside>
   <section className="flex-1 p-4 md:p-6 max-w-[1600px] mx-auto w-full">
    <div className="flex flex-col xl:flex-row gap-3 xl:items-center xl:justify-between mb-5">
     <div><div className="text-xs uppercase tracking-[.25em] text-cyan-300/60">{page}</div><h1 className="text-2xl md:text-3xl font-semibold mt-1">Authorized wireless environment</h1></div>
     <div className="flex flex-wrap items-center gap-2">
      <button onClick={()=>setAuthorized(v=>!v)} className={`px-3 py-2 rounded-lg text-xs font-semibold border ${authorized?'bg-cyan-300/10 text-cyan-200 border-cyan-300/40':'bg-rose-400/10 text-rose-200 border-rose-300/30'}`}>{authorized?'AUTHORIZED MONITORING MODE':'AUTHORIZATION REQUIRED'}</button>
      <button onClick={()=>setPrivacy(v=>!v)} className="px-3 py-2 rounded-lg text-xs border border-white/10 bg-white/5">Privacy {privacy?'ON':'OFF'}</button>
     </div>
    </div>
    {!authorized && <div className="mb-5 rounded-xl border border-amber-300/20 bg-amber-300/5 p-4 text-sm text-amber-100">No telemetry collection can begin until an explicit authorization scope is enabled. The simulator remains available for UI testing only.</div>}
    <div className="grid grid-cols-2 xl:grid-cols-5 gap-3 mb-5">{[
      ['Authorized observations','1,284','+8.2%'],['Active sensors','4','stable'],['Unique devices','27','+3'],['High-risk findings',String(high),'requires review'],['Last sync','14:27:09','UTC−04']
    ].map(([a,b,c])=><div className="glass rounded-xl p-4" key={a}><div className="text-[11px] text-slate-500 uppercase tracking-wider">{a}</div><div className="text-2xl mono mt-2">{b}</div><div className="text-[11px] text-cyan-300/70 mt-1">{c}</div></div>)}</div>
    <div className="grid xl:grid-cols-[1fr_340px] gap-5">
      <div className="glass rounded-2xl overflow-hidden">
       <div className="p-4 border-b border-white/5 flex items-center justify-between"><div className="flex items-center gap-2"><Map size={17}/><span className="font-medium">Live Map</span></div><div className="flex gap-2 text-[11px] text-slate-500"><span>5 observations</span><span>•</span><span>{privacy?'rounded location':'precise location disabled'}</span></div></div>
       <div className="relative min-h-[430px] bg-slate-950/70 grid-bg overflow-hidden">
        <div className="absolute inset-0 opacity-40" style={{background:'radial-gradient(circle at 35% 45%, rgba(34,211,238,.15), transparent 24%),radial-gradient(circle at 68% 60%, rgba(139,92,246,.13), transparent 20%)'}}/>
        {obs.map((x,i)=><div key={x.id} className="absolute" style={{left:`${22+i*14}%`,top:`${30+(i%3)*15}%`}}><div className="absolute -inset-5 rounded-full border border-cyan-300/10 animate-ping"/><div className="h-3 w-3 rounded-full bg-cyan-200 shadow-[0_0_18px_rgba(103,232,249,.9)]"/><div className="mt-2 ml-[-25px] text-[9px] text-cyan-100/70 whitespace-nowrap">{x.label}</div></div>)}
        <div className="absolute bottom-4 left-4 glass rounded-lg px-3 py-2 text-[10px] text-slate-400">Privacy-preserving map • authorization scope enforced</div>
       </div>
      </div>
      <div className="space-y-3">
       <div className="glass rounded-2xl p-4"><div className="flex items-center justify-between mb-4"><span className="font-medium">Intelligence</span><Activity size={16} className="text-cyan-300"/></div>{[['Observation rate','18.4/s'],['Queue depth','12'],['Sensor health','98.7%'],['API health','100%'],['Retention','30 days']].map(([a,b])=><div className="flex justify-between py-2 border-b border-white/5 text-sm" key={a}><span className="text-slate-500">{a}</span><span className="mono text-cyan-100">{b}</span></div>)}</div>
       <div className="glass rounded-2xl p-4"><div className="font-medium mb-3">Compliance guardrails</div><div className="space-y-2 text-xs text-slate-400">{['Passive observation only','No packet content','Identifiers pseudonymized','Precise location gated','Audit logging enabled'].map(x=><div className="flex gap-2 items-center" key={x}><ShieldCheck size={14} className="text-cyan-300"/>{x}</div>)}</div></div>
      </div>
    </div>
    <div className="glass rounded-2xl mt-5 overflow-hidden"><div className="p-4 border-b border-white/5 flex justify-between"><span className="font-medium">Authorized device telemetry</span><span className="text-xs text-slate-500">{obs.length} simulated observations</span></div><div className="overflow-x-auto"><table className="w-full text-sm"><thead className="text-[10px] uppercase tracking-wider text-slate-500"><tr><th className="text-left p-3">Identifier</th><th className="text-left p-3">Technology</th><th className="text-left p-3">Signal</th><th className="text-left p-3">Channel</th><th className="text-left p-3">Risk</th></tr></thead><tbody>{obs.map(x=><tr key={x.id} className="border-t border-white/5"><td className="p-3 mono text-cyan-100">{x.id}</td><td className="p-3 flex gap-2 items-center">{x.tech==='Wi-Fi'?<Wifi size={14}/>:<Bluetooth size={14}/>} {x.tech}</td><td className="p-3 mono">{x.signal} dBm</td><td className="p-3 mono">{x.channel??'—'}</td><td className="p-3"><span className={`px-2 py-1 rounded-full text-[10px] ${x.risk>=50?'bg-rose-400/10 text-rose-200':'bg-cyan-300/10 text-cyan-200'}`}>{x.risk}/100</span></td></tr>)}</tbody></table></div></div>
    <div className="mt-5 glass rounded-xl p-3 flex flex-wrap gap-4 text-[10px] uppercase tracking-wider text-slate-500"><span className="flex items-center gap-2"><ScanLine size={13}/> Simulator</span><span className="flex items-center gap-2"><Gauge size={13}/> 18.4 obs/s</span><span className="flex items-center gap-2"><WifiOff size={13}/> No packet capture</span><span className="ml-auto">Clearwire • Authorized use only</span></div>
   </section>
  </div>
 </main>
}
