// MCQ Generator JavaScript

const boardSelect = document.getElementById('board');
const classSelect = document.getElementById('class');
const subjectSelect = document.getElementById('subject');
const form = document.getElementById('mcqForm');

// Store current MCQ data for PDF download
let currentMCQData = null;

// Load classes when board is selected
boardSelect.addEventListener('change', async function () {
    const board = this.value;
    if (!board) return;

    classSelect.disabled = true;
    subjectSelect.disabled = true;

    classSelect.innerHTML = '<option value="">-- Loading... --</option>';

    try {
        const response = await fetch(`/get_classes/${board}`);
        const classes = await response.json();

        classSelect.innerHTML = '<option value="">-- Select Class --</option>';
        classes.forEach(cls => {
            classSelect.innerHTML += `<option value="${cls}">${cls}</option>`;
        });
        classSelect.disabled = false;
    } catch (error) {
        console.error('Error loading classes:', error);
        classSelect.innerHTML = '<option value="">-- Error loading classes --</option>';
    }
});

// Load subjects when class is selected
classSelect.addEventListener('change', async function () {
    const board = boardSelect.value;
    const classNum = this.value;
    if (!board || !classNum) return;

    subjectSelect.disabled = true;

    subjectSelect.innerHTML = '<option value="">-- Loading... --</option>';

    try {
        const response = await fetch(`/get_subjects/${board}/${classNum}`);
        const subjects = await response.json();

        subjectSelect.innerHTML = '<option value="">-- Select Subject --</option>';
        subjects.forEach(subject => {
            subjectSelect.innerHTML += `<option value="${subject}">${subject}</option>`;
        });
        subjectSelect.disabled = false;
    } catch (error) {
        console.error('Error loading subjects:', error);
        subjectSelect.innerHTML = '<option value="">-- Error loading subjects --</option>';
    }
});

// Load chapters when subject is selected
subjectSelect.addEventListener('change', async function () {
    const board = boardSelect.value;
    const classNum = classSelect.value;
    const subject = this.value;
    const topicContainer = document.getElementById('topicContainer');

    if (!board || !classNum || !subject) return;

    topicContainer.innerHTML = '<p class="placeholder-text">Loading chapters...</p>';
    topicContainer.classList.add('disabled');

    try {
        const response = await fetch(`/get_topics/${board}/${classNum}/${subject}`);
        const topics = await response.json();

        // Clear and populate with checkboxes
        topicContainer.innerHTML = '';
        topicContainer.classList.remove('disabled');

        Object.entries(topics).forEach(([num, name]) => {
            const checkboxHtml = `
                <label class="topic-checkbox">
                    <input type="checkbox" name="topic" value="${num}">
                    <span>${num}. ${name}</span>
                </label>
            `;
            topicContainer.innerHTML += checkboxHtml;
        });
    } catch (error) {
        console.error('Error loading topics:', error);
        topicContainer.innerHTML = '<p class="placeholder-text" style="color: #dc3545;">Error loading chapters</p>';
    }
});

// Handle form submission
form.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Collect selected chapter numbers
    const selectedTopics = Array.from(
        document.querySelectorAll('input[name="topic"]:checked')
    ).map(cb => cb.value);

    // Validate at least one chapter is selected
    if (selectedTopics.length === 0) {
        alert('Please select at least one chapter');
        return;
    }

    const formData = {
        board: boardSelect.value,
        class: classSelect.value,
        subject: subjectSelect.value,
        topics: selectedTopics,  // Send as array
        num_questions: document.getElementById('num_questions').value,
        difficulty_level: document.getElementById('difficulty_level').value
    };

    // Show loading
    document.getElementById('formContainer').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate MCQs');
        }

        // Redirect to results page
        if (data.success && data.redirect) {
            window.location.href = data.redirect;
        } else {
            throw new Error('Unexpected response format');
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('formContainer').style.display = 'block';
        alert('Error: ' + error.message);
    }
});

function displayResults(data) {
    // Store data for PDF download
    currentMCQData = data;

    const topicInfo = document.getElementById('topicInfo');
    const mcqsContainer = document.getElementById('mcqsContainer');

    // Display topic info
    topicInfo.innerHTML = `
        <h3>Topic Information</h3>
        <p><strong>Board:</strong> ${data.topic_info.board}</p>
        <p><strong>Class:</strong> ${data.topic_info.class}</p>
        <p><strong>Subject:</strong> ${data.topic_info.subject}</p>
        <p><strong>Topic:</strong> ${data.topic_info.topic_name}</p>
        <p><strong>Book:</strong> ${data.topic_info.book_name}</p>
    `;

    // Display MCQs
    mcqsContainer.innerHTML = '';
    data.mcqs.forEach((mcq, index) => {
        const mcqCard = document.createElement('div');
        mcqCard.className = 'mcq-card';

        let optionsHtml = '';
        Object.entries(mcq.options).forEach(([key, value]) => {
            const isCorrect = key === mcq.correct_answer;
            optionsHtml += `
                <div class="mcq-option ${isCorrect ? 'correct' : ''}">
                    <strong>${key}.</strong> ${value}
                </div>
            `;
        });

        mcqCard.innerHTML = `
            <div class="mcq-question">Q${index + 1}. ${mcq.question}</div>
            ${optionsHtml}
            <div class="mcq-answer">
                <strong>✓ Correct Answer:</strong> ${mcq.correct_answer}<br>
                <strong>💡 Explanation:</strong> ${mcq.explanation}
            </div>
        `;

        mcqsContainer.appendChild(mcqCard);
    });

    // Show results
    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'block';
}

function resetForm() {
    document.getElementById('formContainer').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    form.reset();
    classSelect.disabled = true;
    subjectSelect.disabled = true;
    document.getElementById('topicContainer').innerHTML = '<p class="placeholder-text">-- Select a subject first --</p>';
    currentMCQData = null;
}

function downloadPDF() {
    if (!currentMCQData) {
        alert('No MCQ data available');
        return;
    }

    // Send data to backend for PDF generation
    fetch('/download_pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(currentMCQData)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }
            return response.blob();
        })
        .then(blob => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `MCQ_${currentMCQData.topic_info.subject}_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error downloading PDF:', error);
            alert('Error downloading PDF: ' + error.message);
        });
}
