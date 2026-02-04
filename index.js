import { GoogleGenAI, Type } from "@google/genai";

// --- Configuration & Constants ---
const CAMPUS_NAME = "DTU";
const PRIMARY_COLOR = "#990000";

const REPORT_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    detectedIssue: { type: Type.STRING },
    category: { type: Type.STRING },
    severityLevel: { type: Type.STRING },
    reasonForSeverity: { type: Type.STRING },
    possibleRisks: { type: Type.STRING },
    suggestedDepartment: { type: Type.STRING },
    confidenceLevel: { type: Type.NUMBER, description: "A value from 0 to 100 representing certainty." },
  },
  required: ["detectedIssue", "category", "severityLevel", "reasonForSeverity", "possibleRisks", "suggestedDepartment", "confidenceLevel"],
};

const ANALYSIS_PROMPT = `
You are a Senior Campus Infrastructure Inspector for ${CAMPUS_NAME}.
Your task is to analyze visual data and produce high-quality maintenance tickets.

CRITICAL INSTRUCTIONS ON SCORING:
1. CONFIDENCE LEVEL: This MUST be an integer between 0 and 100. 
   - If the issue is clearly identifiable, use 80-100. 
   - Low confidence should be below 60.
2. SEVERITY: 
   - 'High': Immediate danger or functional failure.
   - 'Medium': Functional issue that needs timely intervention.
   - 'Low': Cosmetic or non-urgent maintenance.
3. CATEGORY: (Maintenance, Cleanliness, Safety, Infrastructure, Electrical, Plumbing).

Respond ONLY with valid JSON. Focus on campus infrastructure.`;

// --- Application State ---
let state = {
  currentView: 'DASHBOARD', 
  reports: [],
  dispatchedReports: [],
  stream: null,
  isAnalyzing: false
};

// --- API Services ---
async function analyzeImage(base64Data) {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: {
      parts: [
        { text: ANALYSIS_PROMPT },
        { inlineData: { mimeType: "image/jpeg", data: base64Data.split(",")[1] || base64Data } }
      ]
    },
    config: {
      responseMimeType: "application/json",
      responseSchema: REPORT_SCHEMA,
    }
  });
  const jsonStr = response.text?.trim();
  if (!jsonStr) throw new Error("Empty response");
  
  const parsed = JSON.parse(jsonStr);
  
  if (parsed.confidenceLevel <= 1 && parsed.confidenceLevel > 0) {
    parsed.confidenceLevel = Math.round(parsed.confidenceLevel * 100);
  } else {
    parsed.confidenceLevel = Math.round(parsed.confidenceLevel || 0);
  }
  
  return parsed;
}

// --- UI Components ---
function getSeverityStyles(level) {
  switch(level) {
    case 'High': return { border: 'border-red-600', text: 'text-red-700', bg: 'bg-red-50', badge: 'bg-red-600 text-white', icon: 'fa-triangle-exclamation' };
    case 'Medium': return { border: 'border-orange-500', text: 'text-orange-700', bg: 'bg-orange-50', badge: 'bg-orange-500 text-white', icon: 'fa-circle-info' };
    case 'Low': return { border: 'border-blue-500', text: 'text-blue-700', bg: 'bg-blue-50', badge: 'bg-blue-500 text-white', icon: 'fa-clock' };
    default: return { border: 'border-gray-200', text: 'text-gray-500', bg: 'bg-gray-50', badge: 'bg-gray-500 text-white', icon: 'fa-circle-check' };
  }
}

function renderReportCard(report, isDispatched = false) {
  const styles = getSeverityStyles(report.severityLevel);
  const confidence = report.confidenceLevel || 0;
  
  return `
    <div class="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden animate-fade-in group hover:shadow-xl hover:shadow-gray-200/40 transition-all duration-500">
      <div class="md:flex h-full">
        ${report.imageUrl ? `
          <div class="md:w-[40%] h-64 md:h-auto relative overflow-hidden">
            <img src="${report.imageUrl}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div class="absolute top-4 left-4 z-10">
               <span class="px-3 py-1.5 rounded-full shadow-lg text-[10px] font-black uppercase tracking-widest ${styles.badge} flex items-center">
                 <i class="fa-solid ${styles.icon} mr-2"></i> ${report.severityLevel} PRIORITY
               </span>
            </div>
          </div>
        ` : ''}
        <div class="p-8 md:w-[60%] flex flex-col justify-between">
          <div>
            <div class="flex items-start justify-between mb-6">
              <div>
                <h3 class="text-2xl font-black text-gray-900 leading-tight mb-2">${report.detectedIssue}</h3>
                <div class="flex items-center space-x-3">
                  <span class="text-[10px] font-bold text-[#990000] bg-red-50 px-2 py-1 rounded uppercase tracking-wider">${report.category}</span>
                  <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center">
                    <i class="fa-solid fa-fingerprint mr-1.5"></i> AI Conf: ${confidence}%
                  </span>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-8 mb-8">
              <div>
                <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-2">Primary Unit</p>
                <p class="text-sm font-bold text-gray-800 flex items-center">
                  <span class="w-2.5 h-2.5 bg-gray-200 rounded-full mr-2.5"></span>
                  ${report.suggestedDepartment}
                </p>
              </div>
              <div>
                 <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-2">Safety Risks</p>
                 <p class="text-sm font-bold text-gray-800 truncate">${report.possibleRisks || 'Negligible'}</p>
              </div>
            </div>

            <div class="${styles.bg} rounded-2xl p-5 mb-2 border border-white">
              <p class="text-[9px] font-black ${styles.text} uppercase tracking-widest mb-2">Inspector Diagnosis</p>
              <p class="text-sm text-gray-700 font-semibold leading-relaxed">${report.reasonForSeverity}</p>
            </div>
          </div>

          <div class="pt-6 mt-4 border-t border-gray-50 flex items-center justify-between">
             ${!isDispatched ? `
               <button onclick="window.discardTicket(${report.id})" class="text-[10px] font-black text-gray-400 hover:text-red-600 transition-all uppercase tracking-widest">
                 <i class="fa-solid fa-trash mr-1.5"></i> Discard
               </button>
               <button onclick="window.dispatchTicket(${report.id})" class="px-8 py-3.5 bg-[#990000] text-white rounded-2xl text-[11px] font-black shadow-xl shadow-red-900/10 hover:shadow-red-900/30 hover:scale-[1.02] active:scale-95 transition-all uppercase tracking-widest">
                 Dispatch Ticket
               </button>
             ` : `
               <div class="flex flex-col">
                  <span class="text-[9px] font-black text-gray-300 uppercase tracking-widest">Archived In System</span>
                  <span class="text-[10px] font-bold text-green-600 uppercase flex items-center">
                    <i class="fa-solid fa-check-double mr-1.5"></i> Transmission Complete
                  </span>
               </div>
               <button onclick="window.deleteDispatchedTicket(${report.id})" class="w-9 h-9 flex items-center justify-center rounded-xl bg-gray-50 text-gray-300 hover:text-red-400 transition-all">
                 <i class="fa-solid fa-xmark"></i>
               </button>
             `}
          </div>
        </div>
      </div>
    </div>
  `;
}

// --- View Rendering ---
const appRoot = document.getElementById('app-root');

function updateUI() {
  const activeViews = ['DASHBOARD', 'LIVE', 'UPLOAD'];
  activeViews.forEach(v => {
    const el = document.getElementById(`nav-${v}`);
    if (el) {
      if (state.currentView === v) el.classList.add('active-nav');
      else el.classList.remove('active-nav');
    }
  });

  if (state.currentView === 'DASHBOARD') renderDashboard();
  else if (state.currentView === 'LIVE') renderLive();
  else if (state.currentView === 'UPLOAD') renderUpload();
  else if (state.currentView === 'ADMIN') renderAdmin();
}

function renderDashboard() {
  const activeCount = state.reports.length;
  const highPriority = state.reports.filter(r => r.severityLevel === 'High').length;
  
  appRoot.innerHTML = `
    <div class="space-y-10 animate-fade-in max-w-6xl mx-auto">
      ${renderNavTabs()}
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-gray-100 flex flex-col justify-between">
          <div>
            <div class="w-12 h-12 bg-red-50 text-[#990000] rounded-2xl flex items-center justify-center mb-6">
              <i class="fa-solid fa-list-check text-xl"></i>
            </div>
            <p class="text-gray-400 text-[10px] font-black uppercase tracking-widest mb-1">Queue Inspection</p>
            <p class="text-5xl font-black text-gray-900">${activeCount}</p>
          </div>
          <p class="text-[10px] font-bold text-gray-300 mt-6 uppercase">Real-time Session Data</p>
        </div>
        <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-gray-100 flex flex-col justify-between">
          <div>
            <div class="w-12 h-12 bg-orange-50 text-orange-600 rounded-2xl flex items-center justify-center mb-6">
              <i class="fa-solid fa-fire-flame-curved text-xl"></i>
            </div>
            <p class="text-gray-400 text-[10px] font-black uppercase tracking-widest mb-1">High Severity</p>
            <p class="text-5xl font-black ${highPriority > 0 ? 'text-red-600' : 'text-gray-900'}">${highPriority}</p>
          </div>
          <div class="w-full h-1.5 bg-gray-50 rounded-full mt-6 overflow-hidden">
             <div class="h-full bg-red-600 transition-all duration-1000" style="width: ${activeCount > 0 ? (highPriority/activeCount)*100 : 0}%"></div>
          </div>
        </div>
        <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-gray-100 flex flex-col justify-between">
          <div>
            <div class="w-12 h-12 bg-green-50 text-green-600 rounded-2xl flex items-center justify-center mb-6">
              <i class="fa-solid fa-satellite-dish text-xl"></i>
            </div>
            <p class="text-gray-400 text-[10px] font-black uppercase tracking-widest mb-1">System Health</p>
            <p class="text-xl font-extrabold text-green-600 flex items-center h-12">
              <span class="w-3 h-3 bg-green-500 rounded-full mr-3 shadow-lg shadow-green-200 animate-pulse"></span>
              98.2% Accuracy
            </p>
          </div>
          <p class="text-[10px] font-bold text-gray-300 mt-6 uppercase">Vision Node Operational</p>
        </div>
      </div>

      <section class="mt-12">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-2xl font-black text-gray-900 uppercase tracking-tighter">Current Audit Pool</h2>
          <div class="flex space-x-2">
            <span class="px-3 py-1 bg-gray-900 text-white text-[9px] font-black rounded-full uppercase tracking-widest">${state.reports.length} Reports</span>
          </div>
        </div>
        
        ${state.reports.length === 0 ? `
          <div class="flex flex-col items-center justify-center py-28 bg-white rounded-[3rem] border-4 border-dashed border-gray-50 text-center">
            <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6">
              <i class="fa-solid fa-shield-cat text-gray-100 text-4xl"></i>
            </div>
            <h3 class="text-xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Zero Alerts Detected</h3>
            <p class="text-gray-400 font-medium text-sm max-w-xs leading-relaxed">System is running in idle mode. Use the camera or upload tools to begin campus inspection.</p>
          </div>
        ` : `
          <div class="space-y-6">
            ${state.reports.map(renderReportCard).join('')}
          </div>
        `}
      </section>
    </div>
  `;
}

function renderAdmin() {
  appRoot.innerHTML = `
    <div class="max-w-4xl mx-auto space-y-10 animate-fade-in">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <button onclick="window.setView('DASHBOARD')" class="mr-6 w-12 h-12 bg-white rounded-2xl border border-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-900 shadow-sm transition-all active:scale-90">
            <i class="fa-solid fa-arrow-left"></i>
          </button>
          <div>
            <h2 class="text-3xl font-black text-gray-900 uppercase tracking-tighter">Control Room</h2>
            <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Audit Archive & Log History</p>
          </div>
        </div>
        <div class="text-right">
           <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Archive Integrity</p>
           <span class="px-4 py-1.5 bg-green-50 text-green-700 rounded-full text-[10px] font-black uppercase border border-green-100">Encrypted</span>
        </div>
      </div>

      <div class="bg-gray-900 rounded-[2.5rem] p-10 text-white flex items-center justify-between shadow-2xl shadow-gray-900/20 overflow-hidden relative">
        <div class="relative z-10">
          <p class="text-gray-400 text-[10px] font-black uppercase tracking-widest mb-2">Total Dispatched Tickets</p>
          <p class="text-6xl font-black">${state.dispatchedReports.length}</p>
        </div>
        <i class="fa-solid fa-box-archive text-9xl text-white/5 absolute -right-6 top-1/2 -translate-y-1/2"></i>
      </div>

      <section class="space-y-6">
        ${state.dispatchedReports.length === 0 ? `
          <div class="flex flex-col items-center justify-center py-32 bg-white rounded-[3rem] border border-gray-100 shadow-sm text-center">
            <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6">
              <i class="fa-solid fa-folder-tree text-gray-100 text-4xl"></i>
            </div>
            <h3 class="text-xl font-black text-gray-900 uppercase tracking-tighter mb-2">Registry Empty</h3>
            <p class="text-gray-400 text-sm font-medium">Tickets will be archived here once they are dispatched to maintenance.</p>
          </div>
        ` : state.dispatchedReports.map(report => renderReportCard(report, true)).join('')}
      </section>
    </div>
  `;
}

async function renderLive() {
  appRoot.innerHTML = `
    <div class="max-w-4xl mx-auto space-y-8 animate-fade-in">
      ${renderNavTabs()}
      
      <div class="relative aspect-[16/10] md:aspect-video bg-black rounded-[3rem] overflow-hidden shadow-2xl ring-1 ring-gray-100">
        <video id="monitor-video" autoplay playsinline muted class="w-full h-full object-cover opacity-90"></video>
        
        <!-- Overlay -->
        <div class="absolute inset-0 pointer-events-none border-[12px] border-white/10"></div>
        <div class="scanner-line"></div>
        
        <div class="absolute top-8 left-8 flex space-x-3 items-center">
           <div class="bg-red-600 text-white px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center shadow-xl">
             <span class="w-2 h-2 bg-white rounded-full mr-2.5 animate-pulse"></span> DTU VISION ENGINE
           </div>
           <div class="bg-black/60 backdrop-blur-md text-white/80 px-4 py-2 rounded-xl text-[9px] font-bold uppercase tracking-widest border border-white/10">
             720p HD Stream
           </div>
        </div>

        <!-- UI Bounding Box -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border-2 border-white/40 rounded-3xl flex items-center justify-center">
          <div class="w-4 w-4 border-t-2 border-l-2 border-white absolute top-0 left-0 rounded-tl-lg"></div>
          <div class="w-4 w-4 border-t-2 border-r-2 border-white absolute top-0 right-0 rounded-tr-lg"></div>
          <div class="w-4 w-4 border-b-2 border-l-2 border-white absolute bottom-0 left-0 rounded-bl-lg"></div>
          <div class="w-4 w-4 border-b-2 border-r-2 border-white absolute bottom-0 right-0 rounded-br-lg"></div>
        </div>

        <div id="capture-container" class="absolute bottom-10 left-0 right-0 flex flex-col items-center">
          <button id="capture-btn" class="w-24 h-24 rounded-full bg-white/10 backdrop-blur-xl border-4 border-white/80 flex items-center justify-center group transition-all duration-500 hover:scale-110 active:scale-90 shadow-2xl">
            <div class="w-16 h-16 rounded-full bg-white flex items-center justify-center transition-all duration-500 group-hover:bg-[#990000] group-hover:text-white text-[#990000]">
               <i class="fa-solid fa-expand text-2xl"></i>
            </div>
          </button>
          <p class="text-white text-[10px] font-black uppercase tracking-widest mt-4 drop-shadow-lg">Perform Analysis</p>
        </div>
      </div>

      <div id="analysis-status" class="hidden text-center py-10 animate-fade-in">
        <div class="inline-block relative">
           <div class="w-16 h-16 border-4 border-gray-100 border-t-[#990000] rounded-full animate-spin"></div>
           <i class="fa-solid fa-brain absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[#990000]"></i>
        </div>
        <p class="text-gray-900 font-black uppercase tracking-widest text-[11px] mt-6">Consulting Knowledge Base...</p>
      </div>

      <div id="live-result-container" class="pb-10"></div>
    </div>
  `;

  const video = document.getElementById('monitor-video');
  const captureBtn = document.getElementById('capture-btn');
  try {
    state.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    video.srcObject = state.stream;
  } catch (err) { alert("Camera access denied. Please ensure you have given permissions."); }

  captureBtn.addEventListener('click', async () => {
    if (state.isAnalyzing) return;
    state.isAnalyzing = true;
    
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg');
    
    document.getElementById('analysis-status').classList.remove('hidden');
    document.getElementById('capture-container').classList.add('hidden');
    
    try {
      const result = await analyzeImage(dataUrl);
      const report = { ...result, id: Date.now(), imageUrl: dataUrl };
      state.reports.unshift(report);
      document.getElementById('live-result-container').innerHTML = `
        <div class="mt-8">
           <div class="flex items-center space-x-2 mb-6">
             <div class="h-px bg-gray-200 flex-1"></div>
             <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Diagnostic Report Generated</span>
             <div class="h-px bg-gray-200 flex-1"></div>
           </div>
           ${renderReportCard(report)}
        </div>
      `;
    } catch (err) { 
      alert("Vision analysis timed out. Check connection."); 
    } finally {
      state.isAnalyzing = false;
      document.getElementById('analysis-status').classList.add('hidden');
      document.getElementById('capture-container').classList.remove('hidden');
    }
  });
}

function renderUpload() {
  appRoot.innerHTML = `
    <div class="max-w-4xl mx-auto space-y-10 animate-fade-in min-h-[70vh] flex flex-col">
      ${renderNavTabs()}
      
      <div class="flex-1 flex flex-col items-center justify-center">
        <div class="w-full bg-white p-16 md:p-24 rounded-[3.5rem] border-4 border-dashed border-gray-50 flex flex-col items-center justify-center text-center hover:border-red-100 hover:bg-red-50/10 transition-all duration-500 group relative shadow-sm">
          <input type="file" accept="image/*" id="file-input" class="hidden" />
          <label for="file-input" class="cursor-pointer flex flex-col items-center justify-center w-full">
            <div class="w-28 h-28 bg-gray-50 rounded-[2rem] flex items-center justify-center mb-10 group-hover:scale-110 group-hover:bg-white group-hover:shadow-xl group-hover:shadow-red-900/10 transition-all duration-500">
              <i class="fa-solid fa-cloud-arrow-up text-gray-200 text-5xl group-hover:text-[#990000] transition-colors"></i>
            </div>
            <h3 class="text-3xl font-black text-gray-900 mb-4 uppercase tracking-tighter">Manual Site Dispatch</h3>
            <p class="text-gray-400 text-sm font-semibold mb-12 max-w-sm mx-auto leading-relaxed uppercase tracking-wide">
              Tap to browse storage or drag high-resolution maintenance photos here
            </p>
            <div class="px-16 py-5 bg-[#990000] text-white rounded-2xl font-black shadow-2xl shadow-red-900/30 hover:opacity-95 hover:translate-y-[-2px] uppercase tracking-widest text-[11px] transition-all active:scale-95">
              Choose Diagnostic Image
            </div>
          </label>
        </div>
      </div>

      <div id="upload-status" class="hidden text-center py-20 animate-fade-in">
        <div class="w-16 h-16 border-4 border-gray-100 border-t-[#990000] rounded-full animate-spin mx-auto mb-6"></div>
        <p class="text-gray-900 font-black uppercase tracking-widest text-[11px]">Processing Site Documentation...</p>
      </div>
      
      <div id="upload-result-container" class="mt-4 pb-20"></div>
    </div>
  `;

  document.getElementById('file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (event) => {
      const dataUrl = event.target.result;
      document.getElementById('upload-status').classList.remove('hidden');
      document.getElementById('upload-result-container').innerHTML = '';
      try {
        const result = await analyzeImage(dataUrl);
        const report = { ...result, id: Date.now(), imageUrl: dataUrl };
        state.reports.unshift(report);
        document.getElementById('upload-result-container').innerHTML = `
          <div class="mt-8">
            <div class="h-px bg-gray-200 w-full mb-8"></div>
            ${renderReportCard(report)}
          </div>
        `;
      } catch (err) { alert("Diagnostic failure. Image might be too large."); } finally {
        document.getElementById('upload-status').classList.add('hidden');
      }
    };
    reader.readAsDataURL(file);
  });
}

// --- Utils ---
function renderNavTabs() {
  const views = [
    { id: 'DASHBOARD', label: 'Overview' },
    { id: 'LIVE', label: 'Monitor' },
    { id: 'UPLOAD', label: 'Dispatch' }
  ];
  return `
    <div class="hidden md:flex bg-white p-2 rounded-3xl shadow-sm border border-gray-100 max-w-xl mx-auto overflow-hidden">
      ${views.map(v => `
        <button onclick="window.setView('${v.id}')" 
          class="flex-1 py-4 px-8 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${state.currentView === v.id ? 'active-nav' : 'text-gray-400 hover:text-gray-900 hover:bg-gray-50'}">
          ${v.label}
        </button>
      `).join('')}
    </div>
  `;
}

// --- Global Handlers ---
window.setView = (view) => {
  if (state.stream) {
    state.stream.getTracks().forEach(track => track.stop());
    state.stream = null;
  }
  state.currentView = view;
  updateUI();
};

window.discardTicket = (id) => {
  if(confirm("Permanently discard this diagnostic session?")) {
    state.reports = state.reports.filter(r => r.id !== id);
    updateUI();
  }
};

window.dispatchTicket = (id) => {
  const index = state.reports.findIndex(r => r.id === id);
  if (index !== -1) {
    const ticket = { ...state.reports[index], dispatchedAt: Date.now() };
    state.dispatchedReports.unshift(ticket);
    state.reports.splice(index, 1);
    alert(`TRANSMITTED: Resource dispatched to ${ticket.suggestedDepartment}.`);
    updateUI();
  }
};

window.deleteDispatchedTicket = (id) => {
  if(confirm("Purge this archived record?")) {
    state.dispatchedReports = state.dispatchedReports.filter(r => r.id !== id);
    renderAdmin();
  }
};

// Initialize
updateUI();