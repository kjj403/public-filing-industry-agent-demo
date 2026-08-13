let result=null;
const $=id=>document.getElementById(id);

async function loadSample(){
  const sample=await fetch('/api/sample').then(r=>r.json());
  $('companyName').value=sample.company_name;
  $('companyId').value=sample.company_id;
  $('text').value=sample.text;
}

function render(data){
  result=data;
  $('summary').textContent=`${data.company_name}에서 ${data.activities.length}개의 사업 활동을 찾았습니다.`;
  $('activities').innerHTML=data.activities.map(activity=>`
    <article class="activity" data-id="${activity.activity_id}">
      <h3>${activity.activity_id}</h3>
      <div class="evidence">${escapeHtml(activity.source_sentence)}</div>
      ${activity.candidates.map((candidate,index)=>`
        <div class="candidate">
          <input type="radio" name="${activity.activity_id}" value="${candidate.code}" ${index===0?'checked':''}>
          <div><strong>${candidate.code} · ${candidate.label}</strong><div class="chips">${candidate.matched_keywords.map(k=>`<span class="chip">${escapeHtml(k)}</span>`).join('')}</div></div>
          <span class="score">${Math.round(candidate.score*100)}%</span>
        </div>`).join('')}
      <div class="review">
        <select class="action"><option value="approve">승인</option><option value="modify">수정</option><option value="hold">보류</option></select>
        <input class="note" placeholder="검토 메모">
      </div>
    </article>`).join('');
  $('export').disabled=false;
}

function escapeHtml(value){return value.replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}

$('analyze').onclick=async()=>{
  const response=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({company_name:$('companyName').value,company_id:$('companyId').value,text:$('text').value})});
  render(await response.json());
};

$('export').onclick=async()=>{
  const reviews=[...document.querySelectorAll('.activity')].map(card=>({activity_id:card.dataset.id,action:card.querySelector('.action').value,selected_code:card.querySelector('input[type=radio]:checked')?.value||'',note:card.querySelector('.note').value}));
  const reviewed=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({result,reviews})}).then(r=>r.json());
  const blob=new Blob([JSON.stringify(reviewed,null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='reviewed_industry_candidates.json';a.click();URL.revokeObjectURL(a.href);
};

loadSample();

