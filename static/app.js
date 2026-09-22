/* =========================================================
   CAREER AGENT FRONTEND
========================================================= */


/* =========================================================
   ELEMENTS
========================================================= */

const chat =
    document.getElementById("chat");

const messageInput =
    document.getElementById("message");

const sendBtn =
    document.getElementById("sendBtn");

const uploadResumeBtn =
    document.getElementById("uploadResumeBtn");

const resumeInput =
    document.getElementById("resumeInput");

const resetBtn =
    document.getElementById("resetBtn");

const newConversationBtn =
    document.getElementById("newConversationBtn");

const welcome =
    document.getElementById("welcome");


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHTML(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


/* =========================================================
   MARKDOWN
========================================================= */

function formatMarkdown(text) {

    if (!text) {
        return "";
    }


    let value =
        escapeHTML(text);


    const codeBlocks = [];


    value =
        value.replace(
            /```([\s\S]*?)```/g,
            function (_, code) {

                const index =
                    codeBlocks.length;

                codeBlocks.push(
                    `<pre><code>${code.trim()}</code></pre>`
                );

                return `@@CODE${index}@@`;

            }
        );


    /* Headings */

    value =
        value.replace(
            /^### (.*)$/gm,
            "<h3>$1</h3>"
        );

    value =
        value.replace(
            /^## (.*)$/gm,
            "<h2>$1</h2>"
        );

    value =
        value.replace(
            /^# (.*)$/gm,
            "<h1>$1</h1>"
        );


    /* Bold */

    value =
        value.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    /* Italic */

    value =
        value.replace(
            /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
            "<em>$1</em>"
        );


    /* Inline code */

    value =
        value.replace(
            /`([^`\n]+)`/g,
            "<code>$1</code>"
        );


    /* Unordered lists */

    value =
        value.replace(
            /(?:^|\n)((?:[-•]\s+.*(?:\n|$))+)/g,
            function (_, block) {

                const items =
                    block
                        .trim()
                        .split("\n")
                        .map(line =>
                            line.replace(
                                /^[-•]\s+/,
                                ""
                            )
                        )
                        .filter(Boolean);


                return (
                    "<ul>" +
                    items
                        .map(
                            item =>
                                `<li>${item}</li>`
                        )
                        .join("") +
                    "</ul>"
                );

            }
        );


    /* Ordered lists */

    value =
        value.replace(
            /(?:^|\n)((?:\d+\.\s+.*(?:\n|$))+)/g,
            function (_, block) {

                const items =
                    block
                        .trim()
                        .split("\n")
                        .map(line =>
                            line.replace(
                                /^\d+\.\s+/,
                                ""
                            )
                        )
                        .filter(Boolean);


                return (
                    "<ol>" +
                    items
                        .map(
                            item =>
                                `<li>${item}</li>`
                        )
                        .join("") +
                    "</ol>"
                );

            }
        );


    /* Blockquote */

    value =
        value.replace(
            /^&gt;\s?(.*)$/gm,
            "<blockquote>$1</blockquote>"
        );


    /* Paragraph breaks */

    value =
        value.replace(
            /\n{2,}/g,
            "</p><p>"
        );


    value =
        value.replace(
            /\n/g,
            "<br>"
        );


    /*
       Only wrap as paragraph when needed.
    */

    if (
        !value.includes("<h1>") &&
        !value.includes("<h2>") &&
        !value.includes("<h3>") &&
        !value.includes("<ul>") &&
        !value.includes("<ol>") &&
        !value.includes("<pre>")
    ) {

        value =
            `<p>${value}</p>`;

    }


    /* Restore code */

    codeBlocks.forEach(
        (block, index) => {

            value =
                value.replace(
                    `@@CODE${index}@@`,
                    block
                );

        }
    );


    return value;

}


/* =========================================================
   ADD MESSAGE
========================================================= */

function addMessage(
    role,
    text,
    tools = []
) {

    const row =
        document.createElement("div");

    row.className =
        `message-row ${role === "user" ? "user" : "agent"}`;


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const label =
        document.createElement("div");

    label.className =
        "message-label";

    label.textContent =
        role === "user"
            ? "You"
            : "Career Agent";


    const bubble =
        document.createElement("div");

    bubble.className =
        role === "user"
            ? "user-bubble"
            : "agent-bubble";


    if (role === "user") {

        bubble.textContent =
            text;

    } else {

        bubble.innerHTML =
            formatMarkdown(text);

    }


    content.appendChild(label);

    content.appendChild(bubble);

    row.appendChild(content);

    chat.appendChild(row);


    if (
        role !== "user" &&
        Array.isArray(tools) &&
        tools.length
    ) {

        addToolLabels(
            content,
            tools
        );

    }


    chat.scrollTop =
        chat.scrollHeight;


    return bubble;

}


/* =========================================================
   TOOL LABELS
========================================================= */

function addToolLabels(
    parent,
    tools
) {

    const box =
        document.createElement("div");

    box.className =
        "tool-used";


    tools.forEach(tool => {

        const span =
            document.createElement("span");


        if (
            tool ===
            "retrieve_knowledge"
        ) {

            span.textContent =
                "Knowledge base";

        } else if (
            tool === "search_jobs"
        ) {

            span.textContent =
                "Job search";

        } else if (
            tool ===
            "rank_candidate_jobs"
        ) {

            span.textContent =
                "Resume matching";

        } else {

            span.textContent =
                tool;

        }


        box.appendChild(span);

    });


    parent.appendChild(box);

}


/* =========================================================
   HIDE WELCOME
========================================================= */

function hideWelcome() {

    if (welcome) {

        welcome.style.display =
            "none";

    }

}


/* =========================================================
   SEND CHAT MESSAGE
========================================================= */

async function sendMessage(message) {

    message =
        String(message || "").trim();


    if (!message) {
        return;
    }


    hideWelcome();


    addMessage(
        "user",
        message
    );


    messageInput.value =
        "";

    autoResize();


    const thinking =
        addMessage(
            "agent",
            "Thinking..."
        );


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message:
                            message
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Request failed."
            );

        }


        thinking.innerHTML =
            formatMarkdown(
                data.reply ||
                "I couldn't generate a response."
            );


        const tools =
            data.used_tools ||
            data.tools ||
            [];


        if (
            Array.isArray(tools) &&
            tools.length
        ) {

            addToolLabels(
                thinking.parentElement,
                tools
            );

        }


    } catch (error) {

        console.error(
            "CHAT ERROR:",
            error
        );


        thinking.innerHTML = `

            <p>
                <strong>
                    Something went wrong.
                </strong>
            </p>

            <p>
                ${escapeHTML(
                    error.message
                )}
            </p>

        `;

    }


    chat.scrollTop =
        chat.scrollHeight;

}


/* =========================================================
   SEND BUTTON
========================================================= */

if (sendBtn) {

    sendBtn.addEventListener(
        "click",
        () => {

            sendMessage(
                messageInput.value
            );

        }
    );

}


/* =========================================================
   ENTER KEY
========================================================= */

if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage(
                    messageInput.value
                );

            }

        }
    );


    messageInput.addEventListener(
        "input",
        autoResize
    );

}


/* =========================================================
   AUTO RESIZE
========================================================= */

function autoResize() {

    if (!messageInput) {
        return;
    }


    messageInput.style.height =
        "auto";


    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            130
        ) + "px";

}


/* =========================================================
   QUICK ACTION BUTTONS
========================================================= */

function attachQuickButtons() {

    document
        .querySelectorAll(
            "[data-message]"
        )
        .forEach(button => {

            button.onclick =
                function () {

                    const message =
                        this.getAttribute(
                            "data-message"
                        );


                    if (message) {

                        sendMessage(
                            message
                        );

                    }

                };

        });

}


attachQuickButtons();


/* =========================================================
   UPLOAD BUTTON
========================================================= */

if (uploadResumeBtn) {

    uploadResumeBtn.addEventListener(
        "click",
        () => {

            resumeInput.click();

        }
    );

}


/* =========================================================
   RESUME FILE SELECT
========================================================= */

if (resumeInput) {

    resumeInput.addEventListener(
        "change",
        async function () {

            const file =
                this.files[0];


            if (!file) {
                return;
            }


            await uploadResume(
                file
            );

        }
    );

}


/* =========================================================
   UPLOAD RESUME
========================================================= */

async function uploadResume(file) {

    hideWelcome();


    const analyzing =
        addMessage(
            "agent",
            "Analyzing your resume..."
        );


    const formData =
        new FormData();


    /*
       IMPORTANT:
       Flask /api/upload expects "resume".
    */

    formData.append(
        "resume",
        file
    );


    try {

        const response =
            await fetch(
                "/api/upload",
                {
                    method: "POST",

                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Resume upload failed."
            );

        }


        analyzing
            .parentElement
            .parentElement
            .remove();


        console.log(
            "RESUME RESPONSE:",
            data
        );


        const profile =
            data.profile ||
            data;


        const jobs =
            data.recommendations ||
            data.jobs ||
            data.matches ||
            [];


        updateProfile(
            profile
        );


        renderResumeReport(
            profile,
            jobs
        );


    } catch (error) {

        console.error(
            "UPLOAD ERROR:",
            error
        );


        analyzing.innerHTML = `

            <p>
                <strong>
                    Resume upload failed.
                </strong>
            </p>

            <p>
                ${escapeHTML(
                    error.message
                )}
            </p>

        `;

    }


    resumeInput.value =
        "";

}


/* =========================================================
   UPDATE SIDEBAR PROFILE
========================================================= */

function updateProfile(profile) {

    if (!profile) {
        return;
    }


    const name =
        profile.name ||
        profile.full_name ||
        profile.fullName ||
        "Candidate";


    const skills =
        getArray(
            profile.skills
        );


    const education =
        getArray(
            profile.education
        );


    const projects =
        getArray(
            profile.projects
        );


    const certifications =
        getArray(
            profile.certifications
        );


    const profileName =
        document.getElementById(
            "profileName"
        );


    const profileSkills =
        document.getElementById(
            "profileSkills"
        );


    const profileEducation =
        document.getElementById(
            "profileEducation"
        );


    const profileProjects =
        document.getElementById(
            "profileProjects"
        );


    const profileCertifications =
        document.getElementById(
            "profileCertifications"
        );


    if (profileName) {

        profileName.textContent =
            name;

    }


    if (profileSkills) {

        profileSkills.textContent =
            `${skills.length} technical skills`;

    }


    if (profileEducation) {

        profileEducation.textContent =
            `${education.length} education entries`;

    }


    if (profileProjects) {

        profileProjects.textContent =
            `${projects.length} projects`;

    }


    if (profileCertifications) {

        profileCertifications.textContent =
            `${certifications.length} certifications`;

    }

}


/* =========================================================
   ARRAY HELPER
========================================================= */

function getArray(value) {

    if (Array.isArray(value)) {

        return value;

    }


    if (
        typeof value ===
        "string"
    ) {

        return value
            .split(/\n|,/)
            .map(x => x.trim())
            .filter(Boolean);

    }


    return [];

}


/* =========================================================
   RESUME REPORT
========================================================= */

function renderResumeReport(
    profile,
    jobs
) {

    profile =
        profile || {};


    jobs =
        Array.isArray(jobs)
            ? jobs
            : [];


    const name =
        profile.name ||
        profile.full_name ||
        profile.fullName ||
        "Candidate";


    const skills =
        getArray(
            profile.skills
        );


    const education =
        getArray(
            profile.education
        );


    const projects =
        getArray(
            profile.projects
        );


    const certifications =
        getArray(
            profile.certifications
        );


    const experience =
        getArray(
            profile.experience_mentions
        );


    const score =
        calculateProfileScore(
            profile
        );


    const report =
        document.createElement(
            "div"
        );


    report.className =
        "resume-report-row";


    report.innerHTML = `

        <div class="resume-report">


            <!-- =========================================
                 RESUME HEADER
            ========================================== -->

            <div class="resume-header">

                <div>

                    <div class="resume-eyebrow">
                        RESUME ANALYSIS
                    </div>

                    <div class="resume-name">
                        ${escapeHTML(name)}
                    </div>

                    <div class="resume-subtitle">
                        Candidate profile successfully analyzed
                    </div>

                </div>


                <div class="strength-box">

                    <div class="strength-number">
                        ${score}%
                    </div>

                    <div class="strength-label">
                        PROFILE<br>
                        STRENGTH
                    </div>

                </div>

            </div>



            <!-- =========================================
                 CANDIDATE OVERVIEW
            ========================================== -->

            <div class="resume-section">

                <div class="resume-section-title">
                    Candidate profile
                </div>


                <div class="candidate-grid">


                    <div class="candidate-card">

                        <div class="candidate-card-label">
                            Technical Skills
                        </div>

                        <div class="candidate-card-value">
                            ${skills.length} skills detected
                        </div>

                    </div>


                    <div class="candidate-card">

                        <div class="candidate-card-label">
                            Education
                        </div>

                        <div class="candidate-card-value">
                            ${education.length} education entries
                        </div>

                    </div>


                    <div class="candidate-card">

                        <div class="candidate-card-label">
                            Projects
                        </div>

                        <div class="candidate-card-value">
                            ${projects.length} projects detected
                        </div>

                    </div>


                    <div class="candidate-card">

                        <div class="candidate-card-label">
                            Certifications
                        </div>

                        <div class="candidate-card-value">
                            ${certifications.length} certifications
                        </div>

                    </div>


                </div>

            </div>



            <!-- =========================================
                 SKILLS
            ========================================== -->

            <div class="resume-section">

                <div class="resume-section-title">

                    Technical skills

                    <span class="section-count">
                        ${skills.length}
                    </span>

                </div>


                <div class="skills-container">

                    ${
                        skills.length
                        ?
                        skills
                            .map(
                                skill => `
                                    <span class="skill-tag">
                                        ${escapeHTML(skill)}
                                    </span>
                                `
                            )
                            .join("")
                        :
                        `
                            <span class="skill-tag">
                                No skills detected
                            </span>
                        `
                    }

                </div>

            </div>



            <!-- =========================================
                 EDUCATION
            ========================================== -->

            ${
                education.length
                ?
                `

                <div class="resume-section">

                    <div class="resume-section-title">

                        Education

                        <span class="section-count">
                            ${education.length}
                        </span>

                    </div>


                    ${
                        education
                            .map(
                                item => `

                                <div class="resume-list-item">

                                    <div class="resume-list-icon">
                                        🎓
                                    </div>

                                    <div>
                                        ${escapeHTML(item)}
                                    </div>

                                </div>

                                `
                            )
                            .join("")
                    }

                </div>

                `
                :
                ""
            }



            <!-- =========================================
                 EXPERIENCE
            ========================================== -->

            ${
                experience.length
                ?
                `

                <div class="resume-section">

                    <div class="resume-section-title">

                        Experience

                        <span class="section-count">
                            ${experience.length}
                        </span>

                    </div>


                    ${
                        experience
                            .map(
                                item => `

                                <div class="resume-list-item">

                                    <div class="resume-list-icon">
                                        💼
                                    </div>

                                    <div>
                                        ${escapeHTML(item)}
                                    </div>

                                </div>

                                `
                            )
                            .join("")
                    }

                </div>

                `
                :
                ""
            }



            <!-- =========================================
                 PROJECTS
            ========================================== -->

            ${
                projects.length
                ?
                `

                <div class="resume-section">

                    <div class="resume-section-title">

                        Projects

                        <span class="section-count">
                            ${projects.length}
                        </span>

                    </div>


                    ${
                        projects
                            .map(
                                (project, index) => `

                                <div class="project-card">

                                    <div class="project-number">
                                        ${index + 1}
                                    </div>

                                    <div class="project-title">
                                        ${escapeHTML(
                                            typeof project === "string"
                                                ? project
                                                : (
                                                    project.title ||
                                                    project.name ||
                                                    ""
                                                )
                                        )}
                                    </div>

                                </div>

                                `
                            )
                            .join("")
                    }

                </div>

                `
                :
                ""
            }



            <!-- =========================================
                 CERTIFICATIONS
            ========================================== -->

            ${
                certifications.length
                ?
                `

                <div class="resume-section">

                    <div class="resume-section-title">

                        Certifications

                        <span class="section-count">
                            ${certifications.length}
                        </span>

                    </div>


                    ${
                        certifications
                            .map(
                                cert => `

                                <div class="certification-item">

                                    <span>
                                        ✓
                                    </span>

                                    <span>
                                        ${escapeHTML(cert)}
                                    </span>

                                </div>

                                `
                            )
                            .join("")
                    }

                </div>

                `
                :
                ""
            }



            <!-- =========================================
                 JOB MATCHES
            ========================================== -->

            <div class="resume-section jobs-section">

                <div class="resume-section-title">

                    🎯 Top job matches

                    <span class="section-count">
                        ${jobs.length}
                    </span>

                </div>


                <div class="job-results">

                    ${
                        jobs.length
                        ?
                        jobs
                            .slice(0, 10)
                            .map(
                                (job, index) =>
                                    createJobCard(
                                        job,
                                        index
                                    )
                            )
                            .join("")
                        :
                        `
                            <div class="summary-text">
                                No job recommendations available.
                            </div>
                        `
                    }

                </div>

            </div>


        </div>

    `;


    chat.appendChild(
        report
    );


    chat.scrollTop =
        chat.scrollHeight;

}


/* =========================================================
   JOB CARD
========================================================= */

function createJobCard(
    job,
    index
) {

    const title =
        job.title ||
        job.job_title ||
        "Job opportunity";


    const company =
        job.company ||
        "Company not specified";


    const location =
        job.location ||
        "Location not specified";


    /*
       Support multiple possible backend names.
    */

    let score =
        job.match_score ??
        job.match_percentage ??
        job.match_percent ??
        job.match ??
        job.score ??
        job.similarity ??
        0;


    score =
        Number(score);


    if (!Number.isFinite(score)) {

        score = 0;

    }


    score =
        Math.max(
            0,
            Math.min(
                100,
                score
            )
        );


    const matching =
        getArray(
            job.matched_skills ||
            job.matching_skills ||
            job.matchedSkills
        );


    const missing =
        getArray(
            job.missing_skills ||
            job.missingSkills
        );


    let label =
        "Potential match";


    if (score >= 80) {

        label =
            "Strong match";

    } else if (score >= 60) {

        label =
            "Good match";

    } else if (score >= 40) {

        label =
            "Partial match";

    }


    const matchingHTML =
        matching
            .slice(0, 8)
            .map(
                skill => `
                    <span class="match-chip">
                        ✓ ${escapeHTML(skill)}
                    </span>
                `
            )
            .join("");


    const missingHTML =
        missing
            .slice(0, 5)
            .map(
                skill => `
                    <span class="missing-chip">
                        ${escapeHTML(skill)}
                    </span>
                `
            )
            .join("");


    return `

        <div class="job-result-card">


            <div class="job-top">


                <div class="job-rank">
                    #${index + 1}
                </div>


                <div class="job-info">

                    <div class="job-result-title">
                        ${escapeHTML(title)}
                    </div>

                    <div class="job-result-company">
                        ${escapeHTML(company)}
                    </div>

                </div>


                <div class="job-score">

                    <div class="score-number">
                        ${Math.round(score)}%
                    </div>

                    <div class="score-label">
                        MATCH
                    </div>

                </div>


            </div>


            <div class="job-location">

                📍 ${escapeHTML(location)}

            </div>


            ${
                matching.length
                ?
                `

                <div class="job-skills-label">
                    Matching skills
                </div>

                <div class="job-chips">
                    ${matchingHTML}
                </div>

                `
                :
                ""
            }


            ${
                missing.length
                ?
                `

                <div class="job-skills-label">
                    Skills to strengthen
                </div>

                <div class="job-chips">
                    ${missingHTML}
                </div>

                `
                :
                ""
            }


            <div class="match-bar">

                <div
                    class="match-bar-fill"
                    style="width:${score}%"
                ></div>

            </div>


            <div class="job-match-footer">

                <span>
                    ${matching.length} matching skills
                </span>

                <span>
                    ${label}
                </span>

            </div>


        </div>

    `;

}


/* =========================================================
   PROFILE STRENGTH
========================================================= */

function calculateProfileScore(profile) {

    const skills =
        getArray(profile.skills);

    const education =
        getArray(profile.education);

    const projects =
        getArray(profile.projects);

    const certifications =
        getArray(profile.certifications);


    let score = 0;


    score +=
        Math.min(
            skills.length * 3,
            30
        );


    if (education.length > 0) {

        score += 25;

    }


    score +=
        Math.min(
            projects.length * 5,
            25
        );


    score +=
        Math.min(
            certifications.length * 5,
            20
        );


    return Math.min(
        100,
        score
    );

}


/* =========================================================
   RESET
========================================================= */

async function resetSession() {

    try {

        const response =
            await fetch(
                "/api/reset",
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Reset failed."
            );

        }


        chat.innerHTML =
            "";


        resetProfileUI();


        const welcomeDiv =
            document.createElement(
                "div"
            );


        welcomeDiv.className =
            "welcome";


        welcomeDiv.id =
            "welcome";


        welcomeDiv.innerHTML = `

            <div class="welcome-logo">
                C
            </div>

            <h2>
                How can I help with your career?
            </h2>

            <p>
                Upload your resume or ask me about jobs,
                interviews, skills and career preparation.
            </p>

            <div class="suggestions">

                <button
                    type="button"
                    data-message="Find the best jobs for my profile"
                >
                    Find jobs
                </button>

                <button
                    type="button"
                    data-message="Analyze my resume"
                >
                    Analyze resume
                </button>

                <button
                    type="button"
                    data-message="Help me prepare for a technical interview"
                >
                    Interview prep
                </button>

                <button
                    type="button"
                    data-message="Explain RAG and how it works"
                >
                    Learn RAG
                </button>

            </div>

        `;


        chat.appendChild(
            welcomeDiv
        );


        attachQuickButtons();


    } catch (error) {

        console.error(
            "RESET ERROR:",
            error
        );

    }

}


if (resetBtn) {

    resetBtn.addEventListener(
        "click",
        resetSession
    );

}


if (newConversationBtn) {

    newConversationBtn.addEventListener(
        "click",
        resetSession
    );

}


/* =========================================================
   RESET PROFILE UI
========================================================= */

function resetProfileUI() {

    document.getElementById(
        "profileName"
    ).textContent =
        "No resume uploaded";


    document.getElementById(
        "profileSkills"
    ).textContent =
        "Upload your resume to build your profile";


    document.getElementById(
        "profileEducation"
    ).textContent =
        "";


    document.getElementById(
        "profileProjects"
    ).textContent =
        "";


    document.getElementById(
        "profileCertifications"
    ).textContent =
        "";

}


/* =========================================================
   LOAD EXISTING PROFILE
========================================================= */

async function loadProfile() {

    try {

        const response =
            await fetch(
                "/api/profile"
            );


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        const profile =
            data.profile ||
            data;


        if (profile) {

            updateProfile(
                profile
            );

        }

    } catch (error) {

        console.log(
            "No existing profile."
        );

    }

}


/* =========================================================
   INITIALIZE
========================================================= */

loadProfile();

autoResize();

console.log(
    "Career Agent frontend loaded."
);