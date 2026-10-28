const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
let projects = [];

async function api(path, options={}) {
  const res = await fetch(path, options);
  if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
  return res.json();
}

function switchView(id){
  $$('.view').forEach(v=>v.classList.toggle('active',v.id===id));
  $$('.nav').forEach(n=>n.classList.toggle('active',n.dataset.view===id));
}
$$('.nav').forEach(n=>n.onclick=()=>switchView(n.dataset.view));
$('#commandButton').onclick=()=>{switchView('home');$('#chatInput').focus()};

async function loadProjects(){
  projects = await api('/api/projects');
  $('#projects').innerHTML = projects.map(p=>`<article><p class="eyebrow">PROJECT ${p.id}</p><h3>${escapeHtml(p.name)}</h3><p>${escapeHtml(p.description)}</p><small>${p.created_at}</small></article>`).join('');
  $('#uploadProject').innerHTML = '<option value="">No project</option>'+projects.map(p=>`<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');
}
async function loadAgents(){
  const agents=await api('/api/agents');
  $('#agentsGrid').innerHTML=agents.map(a=>`<article><div class="agent-status">● ${a.status}</div><h3>${a.name}</h3><p>${a.role}</p><small>${a.id}</small></article>`).join('');
}
async function loadMemory(){
  const rows=await api('/api/memory');
  $('#memoryList').innerHTML=rows.length?rows.map(m=>`<div class="result"><strong>${m.kind}</strong><p>${escapeHtml(m.content)}</p><small>Project ${m.project_id ?? 'global'} · ${m.created_at}</small></div>`).join(''):'<p>No stored memory yet.</p>';
}
$('#newProject').onclick=async()=>{
  const name=prompt('Project name'); if(!name)return;
  const description=prompt('Project description')||'';
  await api('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,description})});
  await loadProjects();
};
$('#addMemory').onclick=async()=>{
  const content=prompt('Memory to store'); if(!content)return;
  const project_id=projects[0]?.id ?? null;
  await api('/api/memory',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_id,kind:'project',content})});
  await loadMemory();
};
$('#uploadFile').onclick=async()=>{
  const file=$('#fileInput').files[0]; if(!file)return alert('Choose a UTF-8 text file.');
  const fd=new FormData(); fd.append('file',file); if($('#uploadProject').value)fd.append('project_id',$('#uploadProject').value);
  $('#uploadStatus').textContent='Indexing…';
  try{const r=await api('/api/documents',{method:'POST',body:fd});$('#uploadStatus').textContent=`Indexed ${r.name}`}
  catch(e){$('#uploadStatus').textContent=e.message}
};
$('#runSearch').onclick=async()=>{
  const query=$('#searchInput').value.trim(); if(!query)return;
  const rows=await api('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,limit:20})});
  $('#searchResults').innerHTML=rows.length?rows.map(r=>`<div class="result"><strong>${escapeHtml(r.name)}</strong><p>${escapeHtml(r.snippet)}</p><small>Project ${r.project_id ?? 'global'}</small></div>`).join(''):'<p>No evidence found.</p>';
};
$('#sendChat').onclick=async()=>{
  const message=$('#chatInput').value.trim(); if(!message)return;
  $('#chatOutput').textContent='Planning and routing…';
  try{
    const r=await api('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,project_id:projects[0]?.id ?? null,mode:'auto'})});
    $('#chatOutput').textContent=`${r.answer}\n\nRoute: ${r.route.mode}\nAgents: ${r.route.agents.join(', ')}\nProvider: ${r.route.provider}`;
  }catch(e){$('#chatOutput').textContent=e.message}
};
function escapeHtml(v=''){return v.replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
Promise.all([loadProjects(),loadAgents(),loadMemory()]);
