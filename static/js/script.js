// Global variables
let timerInterval = null;
let timerSeconds = 0;
let isPaused = false;
let chatHistory = [];
let currentContext = '';
let currentNotes = '';
let currentSubjectName = '';
let currentSubjectCode = '';
let currentExamType = '';
let currentMindmap = '';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadResources();
    updateStreak();
    loadSessions();
});

// Tab switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// Theme toggle
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    
    if (currentTheme === 'light') {
        body.removeAttribute('data-theme');
        document.querySelector('.theme-toggle').textContent = '🌙';
    } else {
        body.setAttribute('data-theme', 'light');
        document.querySelector('.theme-toggle').textContent = '☀️';
    }
}

// API call helper
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {'Content-Type': 'application/json'},
        };
        if (data) options.body = JSON.stringify(data);
        
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'An error occurred');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message || 'Error occurred. Please try again.', 'error');
        throw error;
    }
}

// Notification system
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 4000);
}

// Study Tab Functions with streaming for notes
async function generateContent() {
    const subjectCode = document.getElementById('subject-code').value.trim().toUpperCase();
    const examType = document.getElementById('exam-type').value;
    
    if (!subjectCode) {
        showNotification('Please enter a subject code', 'error');
        return;
    }
    
    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    
    try {
        // First, generate flashcards and mindmap (non-streaming)
        const result = await apiCall('/api/generate-study-content', 'POST', {
            subject_code: subjectCode,
            exam_type: examType
        });
        
        // Store for PDF generation
        currentSubjectName = result.subject_name;
        currentSubjectCode = result.subject_code;
        currentExamType = result.exam_type;
        currentMindmap = result.mindmap;  // Store mindmap code
        
        // Update context for chat
        currentContext = `Subject: ${result.subject_name} (${subjectCode}), Exam: ${examType}`;
        
        // Display flashcards in dedicated tab
        const flashcardsContent = document.getElementById('flashcards-content');
        displayFlashcards(result.flashcards, flashcardsContent);
        
        // Show flashcard count
        const countBadge = document.getElementById('flashcard-count');
        countBadge.textContent = `${result.flashcards.length} cards`;
        countBadge.classList.remove('hidden');
        
        // Display mind map using Mermaid.js in dedicated tab
        const mindmapContent = document.getElementById('mindmap-content');
        displayMermaidMindMap(result.mindmap, mindmapContent);
        
        // Now stream the study notes to dedicated tab
        const notesContent = document.getElementById('notes-content');
        notesContent.innerHTML = '<p class="streaming-indicator">Generating notes...</p>';
        
        const notesResponse = await fetch('/api/generate-notes/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                subject_code: subjectCode,
                exam_type: examType
            })
        });
        
        if (!notesResponse.ok) {
            throw new Error('Failed to generate notes');
        }
        
        const reader = notesResponse.body.getReader();
        const decoder = new TextDecoder();
        let fullNotes = '';
        let buffer = '';
        
        while (true) {
            const {value, done} = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, {stream: true});
            const lines = buffer.split('\n');
            
            // Keep the last incomplete line in the buffer
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.trim().startsWith('data: ')) {
                    try {
                        const jsonStr = line.trim().substring(6);
                        if (jsonStr) {
                            const data = JSON.parse(jsonStr);
                            if (data.text) {
                                fullNotes += data.text;
                                notesContent.innerHTML = renderMarkdown(fullNotes);
                            }
                            if (data.error) {
                                throw new Error(data.error);
                            }
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
        
        // Store notes for PDF generation
        currentNotes = fullNotes;
        
        // Show download button in Notes tab
        document.getElementById('download-pdf-btn').classList.remove('hidden');
        
        showNotification(`Study material generated for ${result.subject_name}! Check the Notes, Flashcards, and Mind Map tabs.`, 'success');
    } catch (error) {
        console.error('Error generating content:', error);
        showNotification('Error generating content: ' + error.message, 'error');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

// Render markdown-like content
function renderMarkdown(text) {
    // Enhanced markdown rendering with table support
    let html = text;
    
    // Handle markdown tables
    const tableRegex = /\|(.+)\|[\r\n]+\|[\s\-:|]+\|[\r\n]+((?:\|.+\|[\r\n]*)+)/g;
    html = html.replace(tableRegex, (match, header, rows) => {
        const headers = header.split('|').filter(h => h.trim()).map(h => h.trim());
        const rowArray = rows.trim().split('\n').map(row => 
            row.split('|').filter(cell => cell.trim()).map(cell => cell.trim())
        );
        
        let table = '<table class="schedule-table"><thead><tr>';
        headers.forEach(h => table += `<th>${h}</th>`);
        table += '</tr></thead><tbody>';
        
        rowArray.forEach(row => {
            table += '<tr>';
            row.forEach(cell => table += `<td>${cell}</td>`);
            table += '</tr>';
        });
        
        table += '</tbody></table>';
        return table;
    });
    
    // Code blocks (before inline code)
    html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');
    
    // Headings
    html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold and italic (handle bold before italic to avoid conflicts)
    html = html.replace(/\*\*(.+?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/gim, '<em>$1</em>');
    
    // Inline code
    html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');
    
    // Horizontal rule
    html = html.replace(/^---$/gim, '<hr>');
    
    // Lists
    html = html.replace(/^\* (.+$)/gim, '<li>$1</li>');
    html = html.replace(/^\- (.+$)/gim, '<li>$1</li>');
    html = html.replace(/^\d+\. (.+$)/gim, '<li class="numbered">$1</li>');
    
    // Wrap consecutive list items in ul/ol
    html = html.replace(/(<li>.*?<\/li>\n?)+/gis, '<ul>$&</ul>');
    html = html.replace(/(<li class="numbered">.*?<\/li>\n?)+/gis, '<ol>$&</ol>');
    html = html.replace(/ class="numbered"/g, '');
    
    // Paragraphs
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

// Display flashcards
function displayFlashcards(flashcardsJSON, container) {
    try {
        const flashcards = typeof flashcardsJSON === 'string' ? JSON.parse(flashcardsJSON) : flashcardsJSON;
        
        if (!Array.isArray(flashcards)) {
            container.innerHTML = '<p class="placeholder">Error loading flashcards</p>';
            return;
        }
        
        let html = '';
        flashcards.forEach((card, index) => {
            html += `
                <div class="flashcard" onclick="flipCard(${index})">
                    <h4>Card ${index + 1}</h4>
                    <div class="flashcard-question">${card.question}</div>
                    <div class="flashcard-answer" id="answer-${index}">${card.answer}</div>
                    <div class="flashcard-hint">Click to flip</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error parsing flashcards:', error);
        container.innerHTML = '<p class="placeholder">Error loading flashcards</p>';
    }
}

// Flip flashcard
function flipCard(index) {
    const card = document.querySelectorAll('.flashcard')[index];
    card.classList.toggle('flipped');
}

// Display mind map using server-side rendering to image
async function displayMermaidMindMap(mermaidCode, container) {
    try {
        console.log('Displaying mind map...');
        console.log('Mermaid code:', mermaidCode);
        
        // Show loading state with spinner
        container.innerHTML = `
            <div style="text-align: center; padding: 80px;">
                <div class="spinner" style="margin: 0 auto 20px;"></div>
                <p class="placeholder">Rendering mind map as image...</p>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 10px;">
                    This may take a few moments
                </p>
            </div>
        `;
        
        // Validate mermaid code
        if (!mermaidCode || typeof mermaidCode !== 'string') {
            throw new Error('Invalid mermaid code');
        }
        
        // Call backend to generate image
        const response = await fetch('/api/generate-mindmap-image', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                mindmap: mermaidCode
            })
        });
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Failed to generate mindmap image');
        }
        
        // Display the HIGH-QUALITY image
        container.innerHTML = `
            <div style="width: 100%; display: flex; justify-content: center; align-items: center; padding: 20px;">
                <img 
                    src="${result.image}" 
                    alt="Mind Map - High Quality" 
                    style="
                        max-width: 100%; 
                        height: auto; 
                        border-radius: 10px; 
                        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                        image-rendering: -webkit-optimize-contrast;
                        image-rendering: crisp-edges;
                    " 
                />
            </div>
        `;
        
        console.log('Mind map image displayed successfully');
    } catch (error) {
        console.error('Error rendering mind map:', error);
        console.error('Mermaid code was:', mermaidCode);
        container.innerHTML = `
            <div style="text-align: center; padding: 50px;">
                <p class="placeholder">Error loading mind map</p>
                <p style="color: var(--error); font-size: 0.9rem; margin-top: 10px;">
                    ${error.message || 'Please try regenerating the content'}
                </p>
                <details style="margin-top: 15px; text-align: left; max-width: 600px; margin-left: auto; margin-right: auto;">
                    <summary style="cursor: pointer; color: var(--text-secondary);">View Error Details</summary>
                    <pre style="background: var(--surface); padding: 10px; border-radius: 5px; margin-top: 10px; overflow-x: auto; font-size: 0.85rem;">${error.stack || error.message}</pre>
                </details>
            </div>
        `;
    }
}

// Old display mind map function (kept for compatibility)
function displayMindMap(mindmapJSON, container) {
    try {
        const mindmap = typeof mindmapJSON === 'string' ? JSON.parse(mindmapJSON) : mindmapJSON;
        
        function renderNode(node, level = 0) {
            let html = `<div class="mindmap-node" style="margin-left: ${level * 20}px;">`;
            html += `<div class="mindmap-topic">${node.topic}</div>`;
            
            if (node.subtopics && Array.isArray(node.subtopics)) {
                node.subtopics.forEach(subtopic => {
                    html += renderNode(subtopic, level + 1);
                });
            }
            
            html += '</div>';
            return html;
        }
        
        container.innerHTML = renderNode(mindmap);
    } catch (error) {
        console.error('Error parsing mind map:', error);
        container.innerHTML = '<p class="placeholder">Error loading mind map</p>';
    }
}

// Download PDF function
async function downloadPDF() {
    if (!currentNotes) {
        showNotification('No notes available to download', 'error');
        return;
    }
    
    // Prevent multiple clicks
    const downloadBtn = document.getElementById('download-pdf-btn');
    if (downloadBtn.disabled) {
        return;
    }
    
    try {
        // Disable button and show loading state
        downloadBtn.disabled = true;
        const originalText = downloadBtn.textContent;
        downloadBtn.textContent = '⏳ Generating PDF...';
        
        const response = await fetch('/api/download-pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                notes: currentNotes,
                subject_name: currentSubjectName,
                exam_type: currentExamType,
                subject_code: currentSubjectCode,
                mindmap: currentMindmap  // Include mindmap code
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate PDF');
        }
        
        // Create a blob from the response
        const blob = await response.blob();
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        const examTypeText = {
            'internal1': 'Internal1',
            'internal2': 'Internal2',
            'internal3': 'Internal3',
            'semester': 'Semester'
        }[currentExamType] || currentExamType;
        
        a.download = `${currentSubjectCode}_${currentSubjectName.replace(/ /g, '_')}_${examTypeText}_Notes.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('PDF downloaded successfully!', 'success');
        
        // Re-enable button
        downloadBtn.disabled = false;
        downloadBtn.textContent = originalText;
    } catch (error) {
        console.error('Error downloading PDF:', error);
        showNotification('Error downloading PDF: ' + error.message, 'error');
        
        // Re-enable button even on error
        downloadBtn.disabled = false;
        downloadBtn.textContent = '📥 Download PDF';
    }
}

// Chat functions with streaming
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Create a placeholder for the assistant's streaming response
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message assistant';
    const messageParagraph = document.createElement('p');
    messageDiv.appendChild(messageParagraph);
    chatMessages.appendChild(messageDiv);
    
    try {
        // Use streaming endpoint
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                context: currentContext,
                chat_history: chatHistory.slice(-5).join('\n')
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';
        let buffer = '';
        
        while (true) {
            const {value, done} = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, {stream: true});
            const lines = buffer.split('\n');
            
            // Keep the last incomplete line in the buffer
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.trim().startsWith('data: ')) {
                    try {
                        const jsonStr = line.trim().substring(6);
                        if (jsonStr) {
                            const data = JSON.parse(jsonStr);
                            if (data.text) {
                                fullResponse += data.text;
                                messageParagraph.textContent = fullResponse;
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                            }
                            if (data.error) {
                                messageParagraph.textContent = 'Sorry, I encountered an error. Please try again.';
                            }
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e, 'Line:', line);
                    }
                }
            }
        }
        
        // Update chat history
        chatHistory.push(`User: ${message}`);
        chatHistory.push(`Assistant: ${fullResponse}`);
    } catch (error) {
        messageParagraph.textContent = 'Sorry, I encountered an error. Please try again.';
        console.error('Error in streaming chat:', error);
    }
}

function handleChatEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Planner Functions with streaming
async function generateSchedule() {
    const subjects = document.getElementById('subjects-list').value.trim();
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const hoursPerDay = document.getElementById('hours-per-day').value;
    
    // Debug logging
    console.log('Form values:', { subjects, startDate, endDate, hoursPerDay });
    
    if (!subjects) {
        showNotification('Please enter subjects', 'error');
        return;
    }
    
    if (!startDate) {
        showNotification('Please select start date', 'error');
        return;
    }
    
    if (!endDate) {
        showNotification('Please select end date', 'error');
        return;
    }
    
    if (!hoursPerDay || hoursPerDay === '') {
        showNotification('Please select study hours per day', 'error');
        return;
    }
    
    // Validate hours per day (minimum 2)
    if (parseInt(hoursPerDay) < 2) {
        showNotification('Minimum study hours is 2 hours per day', 'error');
        return;
    }
    
    // Validate date range
    const start = new Date(startDate);
    const end = new Date(endDate);
    if (end < start) {
        showNotification('End date must be after start date', 'error');
        return;
    }
    
    document.getElementById('schedule-loading').classList.remove('hidden');
    const scheduleDisplay = document.getElementById('schedule-display');
    scheduleDisplay.innerHTML = '<p class="streaming-indicator">Creating your schedule...</p>';
    
    try {
        // Use streaming endpoint
        const response = await fetch('/api/create-schedule/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                subjects: subjects,
                start_date: startDate,
                end_date: endDate,
                hours_per_day: parseInt(hoursPerDay)
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullSchedule = '';
        let buffer = '';
        
        while (true) {
            const {value, done} = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, {stream: true});
            const lines = buffer.split('\n');
            
            // Keep the last incomplete line in the buffer
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.trim().startsWith('data: ')) {
                    try {
                        const jsonStr = line.trim().substring(6);
                        if (jsonStr) {
                            const data = JSON.parse(jsonStr);
                            if (data.text) {
                                fullSchedule += data.text;
                                scheduleDisplay.innerHTML = renderMarkdown(fullSchedule);
                            }
                            if (data.done) {
                                showNotification('Schedule created successfully!', 'success');
                            }
                            if (data.error) {
                                throw new Error(data.error);
                            }
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error generating schedule:', error);
        showNotification('Error generating schedule', 'error');
    } finally {
        document.getElementById('schedule-loading').classList.add('hidden');
    }
}

// Timer Functions
function startTimer() {
    const minutes = parseInt(document.getElementById('timer-minutes').value) || 25;
    
    if (!isPaused) {
        timerSeconds = minutes * 60;
    }
    
    isPaused = false;
    
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    timerInterval = setInterval(() => {
        if (timerSeconds > 0) {
            timerSeconds--;
            updateTimerDisplay();
        } else {
            clearInterval(timerInterval);
            timerComplete();
        }
    }, 1000);
}

function pauseTimer() {
    isPaused = true;
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function resetTimer() {
    isPaused = false;
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    const minutes = parseInt(document.getElementById('timer-minutes').value) || 25;
    timerSeconds = minutes * 60;
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const minutes = Math.floor(timerSeconds / 60);
    const seconds = timerSeconds % 60;
    const display = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timer').textContent = display;
}

function timerComplete() {
    showNotification('🎉 Pomodoro session complete! Take a break.', 'success');
    
    // Save session
    const minutes = parseInt(document.getElementById('timer-minutes').value) || 25;
    saveSession(minutes);
    
    // Play notification sound (if available)
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Pomodoro Complete!', {
            body: 'Great work! Time for a break.',
            icon: '/static/images/icon.png'
        });
    }
}

async function saveSession(duration) {
    try {
        const result = await apiCall('/api/save-session', 'POST', {
            duration: duration,
            timestamp: new Date().toISOString(),
            subject: currentContext || 'General Study'
        });
        
        // Add to sessions list
        addSessionToList(result.session);
        
        // Update streak
        updateStreak();
        
        // Save to localStorage
        let sessions = JSON.parse(localStorage.getItem('study_sessions') || '[]');
        sessions.push(result.session);
        localStorage.setItem('study_sessions', JSON.stringify(sessions));
    } catch (error) {
        console.error('Error saving session:', error);
    }
}

function loadSessions() {
    const sessions = JSON.parse(localStorage.getItem('study_sessions') || '[]');
    sessions.slice(-10).reverse().forEach(session => {
        addSessionToList(session);
    });
}

function addSessionToList(session) {
    const sessionsList = document.getElementById('sessions-list');
    
    // Remove placeholder if exists
    const placeholder = sessionsList.querySelector('.placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    const sessionDiv = document.createElement('div');
    sessionDiv.className = 'session-item';
    
    const date = new Date(session.timestamp);
    const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    sessionDiv.innerHTML = `
        <div>
            <strong>${session.subject}</strong>
            <br><small>${dateStr}</small>
        </div>
        <div>${session.duration} min</div>
    `;
    
    sessionsList.insertBefore(sessionDiv, sessionsList.firstChild);
}

function updateStreak() {
    const sessions = JSON.parse(localStorage.getItem('study_sessions') || '[]');
    
    if (sessions.length === 0) {
        document.getElementById('streak-count').textContent = '0 days';
        return;
    }
    
    // Calculate streak
    let streak = 0;
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);
    
    const sessionDates = sessions.map(s => {
        const d = new Date(s.timestamp);
        d.setHours(0, 0, 0, 0);
        return d.getTime();
    });
    
    const uniqueDates = [...new Set(sessionDates)].sort((a, b) => b - a);
    
    for (let date of uniqueDates) {
        const dayDiff = Math.floor((currentDate - date) / (1000 * 60 * 60 * 24));
        
        if (dayDiff === streak) {
            streak++;
        } else {
            break;
        }
    }
    
    document.getElementById('streak-count').textContent = `${streak} day${streak !== 1 ? 's' : ''}`;
}

// Resources Functions
// Download PYQ function
async function downloadPYQ() {
    const subjectCode = document.getElementById('pyq-subject').value.trim().toUpperCase();
    const year = document.getElementById('pyq-year').value;
    const displayDiv = document.getElementById('pyq-display');
    
    // Validation
    if (!subjectCode) {
        showNotification('Please enter a subject code', 'error');
        return;
    }
    
    if (!year) {
        showNotification('Please select a year', 'error');
        return;
    }
    
    // Show loading
    displayDiv.innerHTML = '<p class="placeholder">Searching for PYQ...</p>';
    
    try {
        // Construct the download URL
        const downloadUrl = `/api/download-pyq/${subjectCode}/${year}`;
        
        // Fetch to check if file exists
        const response = await fetch(downloadUrl);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'PYQ not found');
        }
        
        // Create a temporary anchor element to trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${subjectCode}_${year}.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
        displayDiv.innerHTML = `
            <div style="background: var(--success); color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-weight: 600;">✓ Downloaded Successfully!</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">${subjectCode} - ${year}</p>
            </div>
        `;
        
        showNotification(`PYQ downloaded: ${subjectCode} (${year})`, 'success');
    } catch (error) {
        console.error('Error downloading PYQ:', error);
        displayDiv.innerHTML = `
            <div style="background: var(--error); color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-weight: 600;">✗ Not Found</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">${error.message}</p>
            </div>
        `;
        showNotification(error.message, 'error');
    }
}

// Old fetchPYQs function (kept for compatibility)
async function fetchPYQs() {
    const subjectCode = document.getElementById('pyq-subject').value.trim().toUpperCase();
    const examType = document.getElementById('pyq-exam-type').value;
    
    if (!subjectCode) {
        showNotification('Please enter a subject code', 'error');
        return;
    }
    
    try {
        let url = `/api/get-pyqs?subject_code=${subjectCode}`;
        if (examType) {
            url += `&exam_type=${examType}`;
        }
        
        const result = await apiCall(url);
        
        displayPYQs(result.pyqs, result.subject_name);
        showNotification(`PYQs loaded for ${result.subject_name}`, 'success');
    } catch (error) {
        document.getElementById('pyq-display').innerHTML = '<p class="placeholder">No PYQs found for this subject</p>';
    }
}

function displayPYQs(pyqs, subjectName) {
    const container = document.getElementById('pyq-display');
    
    if (!pyqs || (typeof pyqs === 'object' && Object.keys(pyqs).length === 0)) {
        container.innerHTML = '<p class="placeholder">No PYQs available</p>';
        return;
    }
    
    let html = '<div class="pyq-section">';
    
    // If pyqs is an object with exam types
    if (typeof pyqs === 'object' && !Array.isArray(pyqs)) {
        for (const [examType, years] of Object.entries(pyqs)) {
            html += `<h4>${examType.toUpperCase()}</h4>`;
            years.forEach(yearData => {
                html += `<div class="pyq-year">`;
                html += `<h5>Year: ${yearData.year}</h5>`;
                yearData.questions.forEach(q => {
                    html += `<div class="pyq-question">${q}</div>`;
                });
                html += `</div>`;
            });
        }
    } else if (Array.isArray(pyqs)) {
        // If pyqs is an array of year data
        pyqs.forEach(yearData => {
            html += `<div class="pyq-year">`;
            html += `<h4>Year: ${yearData.year}</h4>`;
            yearData.questions.forEach(q => {
                html += `<div class="pyq-question">${q}</div>`;
            });
            html += `</div>`;
        });
    }
    
    html += '</div>';
    container.innerHTML = html;
}

async function loadResources() {
    try {
        const result = await apiCall('/api/get-resources');
        
        // Display links
        const linksContainer = document.getElementById('links-list');
        let linksHTML = '';
        result.resources.links.forEach(link => {
            linksHTML += `
                <div class="resource-item">
                    <a href="${link.url}" target="_blank">${link.title}</a>
                    <span class="resource-category">${link.category}</span>
                </div>
            `;
        });
        linksContainer.innerHTML = linksHTML;
        
        // Display certifications
        const certsContainer = document.getElementById('certifications-list');
        let certsHTML = '';
        result.resources.certifications.forEach(cert => {
            certsHTML += `
                <div class="resource-item">
                    <strong>${cert.name}</strong>
                    <br><small>Provider: ${cert.provider}</small>
                    <span class="resource-category">${cert.category}</span>
                </div>
            `;
        });
        certsContainer.innerHTML = certsHTML;
    } catch (error) {
        console.error('Error loading resources:', error);
    }
}

// Request notification permission on load
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
