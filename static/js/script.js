const boardSelect = document.getElementById('board');
const classSelect = document.getElementById('class');
const subjectSelect = document.getElementById('subject');
const topicSelect = document.getElementById('topic');
const subtopicsSelect = document.getElementById('subtopics');
const form = document.getElementById('mcqForm');

// Load classes when board is selected
boardSelect.addEventListener('change', async function () {
    const board = this.value;
    if (!board) return;

    classSelect.disabled = true;
    subjectSelect.disabled = true;
    topicSelect.disabled = true;
    subtopicsSelect.disabled = true;
    subtopicsSelect.innerHTML = '<option value="">-- Select Topic First --</option>';

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
    topicSelect.disabled = true;
    subtopicsSelect.disabled = true;
    subtopicsSelect.innerHTML = '<option value="">-- Select Topic First --</option>';

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

// Load topics when subject is selected
subjectSelect.addEventListener('change', async function () {
    const board = boardSelect.value;
    const classNum = classSelect.value;
    const subject = this.value;
    if (!board || !classNum || !subject) return;

    topicSelect.disabled = true;
    subtopicsSelect.disabled = true;
    subtopicsSelect.innerHTML = '<option value="">-- Select Topic First --</option>';
    topicSelect.innerHTML = '<option value="">-- Loading... --</option>';

    try {
        const response = await fetch(`/get_topics/${board}/${classNum}/${subject}`);
        const topics = await response.json();

        topicSelect.innerHTML = '<option value="">-- Select Topic --</option>';
        Object.entries(topics).forEach(([num, name]) => {
            topicSelect.innerHTML += `<option value="${num}">${num}. ${name}</option>`;
        });
        topicSelect.disabled = false;
    } catch (error) {
        console.error('Error loading topics:', error);
        topicSelect.innerHTML = '<option value="">-- Error loading topics --</option>';
    }
});

// Load subtopics when topic is selected
topicSelect.addEventListener('change', async function () {
    const board = boardSelect.value;
    const classNum = classSelect.value;
    const subject = subjectSelect.value;
    const topic = this.value;

    if (!board || !classNum || !subject || !topic) return;

    subtopicsSelect.disabled = true;
    subtopicsSelect.innerHTML = '<option value="">-- Loading... --</option>';

    try {
        const response = await fetch(`/get_subtopics/${board}/${classNum}/${subject}/${topic}`);
        const subtopics = await response.json();

        subtopicsSelect.innerHTML = '';
        if (subtopics.length === 0) {
            subtopicsSelect.innerHTML = '<option value="">No subtopics available</option>';
        } else {
            subtopics.forEach(sub => {
                subtopicsSelect.innerHTML += `<option value="${sub.id}">${sub.id === 'all' ? '' : sub.id + ' - '}${sub.name}</option>`;
            });
        }
        subtopicsSelect.disabled = false;
    } catch (error) {
        console.error('Error loading subtopics:', error);
        subtopicsSelect.innerHTML = '<option value="">-- Error loading subtopics --</option>';
    }
});

// Handle form submission
form.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Get selected subtopics
    const selectedSubtopics = Array.from(subtopicsSelect.selectedOptions).map(option => option.value);

    const formData = {
        board: boardSelect.value,
        class: classSelect.value,
        subject: subjectSelect.value,
        topic: topicSelect.value,
        subtopics: selectedSubtopics,
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

        displayResults(data);
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('formContainer').style.display = 'block';
        alert('Error: ' + error.message);
    }
});

function displayResults(data) {
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
    topicSelect.disabled = true;
    subtopicsSelect.disabled = true;
    subtopicsSelect.innerHTML = '<option value="">-- Select Topic First --</option>';
}
