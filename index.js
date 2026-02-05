import { GoogleGenAI, Type } from "@google/genai";
import supabase from "./supabase.js";
import {useEffect, useState} from "react";

const[fetchError, setFetchError] = useState(null);
const[tickets, setTickets] = useState(null);
useEffect(()=>{
  const fetchtickets= async()=>{
    const {data,error}= await supabase.from('tickets').select();
    if(error){
      setFetchError("Could not fetch data");
      setTickets(null);
    }
    if(data){
      setTickets(data);
      setFetchError(null);
    }
  }
  fetchtickets();
},[]);


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

let state = {
  currentView: 'DASHBOARD', 
  reports: [],
  dispatchedReports: [],
  stream: null,
  isAnalyzing: false
};


async function analyzeImage(base64Data) {
  const loc={};
  try{
    try{
      const loc=await location();
    }
    catch(er){
      console.log("location not found");
      const loc={lat:0,long:0};
    }
    console.log("PRIMARY MODEL");
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    if(!ai){
      console.log("API KEY ERROR");
  }
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: {
        parts: [
          { text: ANALYSIS_PROMPT },
          {inlineData: { mimeType: "image/jpeg", data: base64Data.split(",")[1] || base64Data } }
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
  
    return {...parsed,lat:loc.lat,long:loc.long };
  }
  catch(err){
    console.log("SECONDARY MODEL");
    try{
      const loc=await location();
    }
    catch(er){
      console.log("location not found");
      const loc={lat:0,long:0};
    }
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    if(!ai){
      console.log("API KEY ERROR");
  }
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
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
  
    return {...parsed,lat:loc.lat,long:loc.long };
  }
}


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


async function updateUI() {
  const activeViews = ['DASHBOARD', 'LIVE', 'UPLOAD'];
  activeViews.forEach(v => {

    const el = document.getElementById(`nav-${v}`);
    if (el) {
      if (state.currentView === v) el.classList.add('active-nav');
      else el.classList.remove('active-nav');
    }
    // Desktop Nav
    const btn = document.getElementById(`nav-btn-${v}`);
    if (btn) {
      if (state.currentView === v) {
        btn.classList.add('active-nav');
        btn.classList.remove('text-gray-400', 'hover:text-gray-900', 'hover:bg-gray-50');
      } else {
        btn.classList.remove('active-nav');
        btn.classList.add('text-gray-400', 'hover:text-gray-900', 'hover:bg-gray-50');
      }
    }
  });

  document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
  
  const desktopNav = document.getElementById('desktop-nav');
  if (state.currentView === 'ADMIN') desktopNav.classList.add('hidden');
  else desktopNav.classList.remove('hidden');

  if (state.currentView === 'DASHBOARD') {
    document.getElementById('view-dashboard').classList.remove('hidden');
    updateDashboardData();
  } else if (state.currentView === 'LIVE') {
    document.getElementById('view-live').classList.remove('hidden');
    await setupLiveView();
  } else if (state.currentView === 'UPLOAD') {
    document.getElementById('view-upload').classList.remove('hidden');
    // Upload view is static, no data update needed on switch
  } else if (state.currentView === 'ADMIN') {
    document.getElementById('view-admin').classList.remove('hidden');
    updateAdminData();
  }
}

function updateDashboardData() {
  const activeCount = state.reports.length;
  const highPriority = state.reports.filter(r => r.severityLevel === 'High').length;
  
  document.getElementById('dash-queue-count').textContent = activeCount;
  const highCountEl = document.getElementById('dash-high-count');
  highCountEl.textContent = highPriority;
  highCountEl.className = `text-5xl font-black ${highPriority > 0 ? 'text-red-600' : 'text-gray-900'}`;
  
  const percentage = activeCount > 0 ? (highPriority/activeCount)*100 : 0;
  document.getElementById('dash-severity-bar').style.width = `${percentage}%`;
  
  document.getElementById('dash-total-badge').textContent = `${activeCount} Reports`;
  
  const container = document.getElementById('dash-reports-container');
  if (state.reports.length === 0) {
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center py-28 bg-white rounded-[3rem] border-4 border-dashed border-gray-50 text-center">
        <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6">
          <i class="fa-solid fa-shield-cat text-gray-100 text-4xl"></i>
        </div>
        <h3 class="text-xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Zero Alerts Detected</h3>
        <p class="text-gray-400 font-medium text-sm max-w-xs leading-relaxed">System is running in idle mode. Use the camera or upload tools to begin campus inspection.</p>
      </div>`;
  } else {
    container.innerHTML = state.reports.map(r => renderReportCard(r)).join('');
  }
}

function updateAdminData() {
  document.getElementById('admin-dispatched-count').textContent = state.dispatchedReports.length;
  
  const container = document.getElementById('admin-reports-container');
  if (state.dispatchedReports.length === 0) {
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center py-32 bg-white rounded-[3rem] border border-gray-100 shadow-sm text-center">
        <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6">
          <i class="fa-solid fa-folder-tree text-gray-100 text-4xl"></i>
        </div>
        <h3 class="text-xl font-black text-gray-900 uppercase tracking-tighter mb-2">Registry Empty</h3>
        <p class="text-gray-400 text-sm font-medium">Tickets will be archived here once they are dispatched to maintenance.</p>
      </div>`;
  } else {
    container.innerHTML = state.dispatchedReports.map(report => renderReportCard(report, true)).join('');
  }
}

async function setupLiveView() {
  const video = document.getElementById('monitor-video');
  
  try {
    state.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    video.srcObject = state.stream;
  } catch (err) { alert("Camera access denied. Please ensure you have given permissions."); }
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
    updateAdminData();
  }
};

document.getElementById('capture-btn').addEventListener('click', async () => {
  if (state.isAnalyzing) return;
  state.isAnalyzing = true;
  
  const video = document.getElementById('monitor-video');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const dataUrl = canvas.toDataURL('image/jpeg');
  
  document.getElementById('analysis-status').classList.remove('hidden');
  document.getElementById('capture-container').classList.add('hidden');
  
  try {
    const result = await analyzeImage(dataUrl);
    const report = { ...result, id: Date.now(), imageUrl: dataUrl, latitude: result.lat, longitude: result.long };
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
    console.log(err);
  } finally {
    state.isAnalyzing = false;
    document.getElementById('analysis-status').classList.add('hidden');
    document.getElementById('capture-container').classList.remove('hidden');
  }
});

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

function location() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported by this browser."));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => resolve({ lat: position.coords.latitude, long: position.coords.longitude }),
      (error) => reject(error)
    );
  });
}

// 2. Start App
updateUI();