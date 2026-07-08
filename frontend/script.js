document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const youtubeInput = document.getElementById('youtube-url');
    
    const inputSection = document.querySelector('.input-section');
    const loadingSection = document.getElementById('loading-state');
    const optionsSection = document.getElementById('options-state');
    const resultSection = document.getElementById('result-state');
    
    const loadingText = document.getElementById('loading-text');
    const optionsContainer = document.getElementById('options-container');
    const trackHistoryContainer = document.getElementById('track-history-container');
    
    // Store variables between steps
    let currentFileId = "";
    let currentVideoDuration = 0;
    
    // Tweak variables
    let currentOriginalPrompt = "";
    let currentOriginalTitle = "";
    let activeTweaks = new Set();
    const tweakBtns = document.querySelectorAll('.tweak-btn');
    const regenerateBtn = document.getElementById('re-generate-btn');
    
    tweakBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const group = btn.closest('.tweak-group');
            if (btn.classList.contains('selected')) {
                btn.classList.remove('selected');
                activeTweaks.delete(btn.dataset.tweak);
            } else {
                group.querySelectorAll('.tweak-btn').forEach(sibling => {
                    sibling.classList.remove('selected');
                    activeTweaks.delete(sibling.dataset.tweak);
                });
                btn.classList.add('selected');
                activeTweaks.add(btn.dataset.tweak);
            }
            
            if (activeTweaks.size > 0) {
                regenerateBtn.classList.remove('hidden');
            } else {
                regenerateBtn.classList.add('hidden');
            }
        });
    });
    
    regenerateBtn.addEventListener('click', () => {
        if (activeTweaks.size === 0) return;
        
        let appendedKeywords = Array.from(activeTweaks).join(', ');
        // Prepend tweaks to the front so the AI gives them higher priority
        let tweakedPrompt = appendedKeywords + ', ' + currentOriginalPrompt;
        
        regenerateBtn.classList.add('hidden');
        
        generateMusicFromOption({
            title: currentOriginalTitle + ' (튜닝됨)',
            description: '사용자의 튜닝 설정이 반영된 새로운 버전입니다.',
            lyria_prompt: tweakedPrompt
        });
    });
    
    generateBtn.addEventListener('click', async () => {
        const url = youtubeInput.value.trim();
        
        if (!url) {
            alert('유튜브 영상 링크를 입력해주세요.');
            youtubeInput.focus();
            return;
        }

        if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
            alert('올바른 유튜브 링크 형식이 아닙니다.');
            return;
        }

        // 1. Transition to Loading State
        inputSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        loadingText.textContent = '영상을 분석하고 맞춤형 음악 컨셉을 기획하고 있습니다... (최대 1분 소요)';
        
        try {
            // Call the FastAPI Backend - Analyze Step
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    youtube_url: url
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || '서버 에러가 발생했습니다.');
            }

            const data = await response.json();
            
            currentFileId = data.file_id;
            currentVideoDuration = data.video_duration;
            
            // 2. Show Options
            showOptions(data.options);
            
        } catch (error) {
            alert('오류 발생: ' + error.message);
            loadingSection.classList.add('hidden');
            inputSection.classList.remove('hidden');
        }
    });

    function showOptions(options) {
        loadingSection.classList.add('hidden');
        optionsSection.classList.remove('hidden');
        
        optionsContainer.innerHTML = '';
        
        options.forEach((opt, index) => {
            const card = document.createElement('div');
            card.className = 'option-card';
            
            card.innerHTML = `
                <div class="option-title">${opt.title}</div>
                <div class="option-desc">${opt.description}</div>
                <button class="option-generate-btn">이 컨셉으로 작곡하기 <i class="fa-solid fa-music"></i></button>
            `;
            
            const btn = card.querySelector('button');
            btn.addEventListener('click', () => {
                generateMusicFromOption(opt);
            });
            
            optionsContainer.appendChild(card);
        });
    }
    
    async function generateMusicFromOption(option) {
        currentOriginalTitle = option.title;
        currentOriginalPrompt = option.lyria_prompt;
        
        // Stop playing any existing audio players
        document.querySelectorAll('audio').forEach(audio => audio.pause());
        
        // Disable option buttons while loading
        document.querySelectorAll('.option-generate-btn').forEach(btn => btn.disabled = true);
        
        resultSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        loadingText.textContent = `"${option.title}" 컨셉으로 Lyria 3 인공지능이 작곡을 진행 중입니다... (최대 1~2분 소요)`;
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_id: currentFileId,
                    video_duration: currentVideoDuration,
                    lyria_prompt: option.lyria_prompt
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || '서버 에러가 발생했습니다.');
            }

            const data = await response.json();
            
            // 3. Show Result
            showResult(option.title, option.lyria_prompt, data.audio_url);
            
        } catch (error) {
            alert('오류 발생: ' + error.message);
            loadingSection.classList.add('hidden');
            document.querySelectorAll('.option-generate-btn').forEach(btn => btn.disabled = false);
        }
    }

    function showResult(title, prompt, audioUrl) {
        loadingSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        
        // Re-enable option buttons
        document.querySelectorAll('.option-generate-btn').forEach(btn => btn.disabled = false);
        
        // Add cache-buster so the browser doesn't play an old cached mp3 (just in case)
        const finalAudioUrl = audioUrl + '?t=' + new Date().getTime();
        
        // Create a new track card
        const card = document.createElement('div');
        card.className = 'track-card';
        
        card.innerHTML = `
            <h3>${title}</h3>
            <p class="generated-prompt">"${prompt}"</p>
            <div class="audio-player">
                <audio controls>
                    <source src="${finalAudioUrl}" type="audio/mpeg">
                    브라우저가 오디오를 지원하지 않습니다.
                </audio>
            </div>
            <button class="download-btn">
                <i class="fa-solid fa-download"></i> 개별 음원 다운로드
            </button>
        `;
        
        const audioEl = card.querySelector('audio');
        const dlBtn = card.querySelector('.download-btn');
        
        dlBtn.addEventListener('click', async () => {
            try {
                dlBtn.disabled = true;
                dlBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 다운로드 중...';
                
                const response = await fetch(finalAudioUrl);
                const blob = await response.blob();
                const blobUrl = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = blobUrl;
                a.download = 'VideoVibe_BGM.mp3';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(blobUrl);
            } catch (err) {
                console.error("Download failed:", err);
                window.open(finalAudioUrl, '_blank');
            } finally {
                dlBtn.disabled = false;
                dlBtn.innerHTML = '<i class="fa-solid fa-download"></i> 개별 음원 다운로드';
            }
        });
        
        // Prepend to history container so the newest is at the top
        trackHistoryContainer.prepend(card);
        
        // Auto play the newest track
        audioEl.load();
        audioEl.play().catch(e => console.log("Auto-play blocked", e));
    }
});
