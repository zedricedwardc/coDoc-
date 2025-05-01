document.addEventListener("DOMContentLoaded", () => {
  // Make sure the refactor modal is hidden when the page loads
  const refactorModal = document.getElementById("refactor-modal")
  if (refactorModal) {
    refactorModal.classList.add("hidden")
  }

  // Initialize CodeMirror for code editor
  const editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
    mode: "python",
    theme: "dracula",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    autoCloseBrackets: true,
    matchBrackets: true,
    lineWrapping: true,
  })

  // Initialize CodeMirror for refactored code
  const refactoredEditor = CodeMirror.fromTextArea(document.getElementById("refactored-code"), {
    mode: "python",
    theme: "dracula",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    autoCloseBrackets: true,
    matchBrackets: true,
    lineWrapping: true,
    readOnly: false,
  })

  // Set initial height
  editor.setSize(null, "100%")
  refactoredEditor.setSize(null, "100%")

  // Elements
  const languageSelect = document.getElementById("language")
  const analyzeBtn = document.getElementById("analyze-btn")
  const resultsContainer = document.getElementById("results-container")
  const resultsPlaceholder = document.getElementById("results-placeholder")
  const loadingOverlay = document.getElementById("loading-overlay")
  const loadingMessage = document.getElementById("loading-message")
  const metricsGrid = document.getElementById("metrics-grid")
  const complexityTable = document.getElementById("complexity-table")
  const aiContent = document.getElementById("ai-content")

  // Refactor elements
  const refactorBtn = document.getElementById("refactor-btn")
  const closeRefactorModalBtn = document.getElementById("close-refactor-modal")
  const acceptRefactorBtn = document.getElementById("accept-refactor")
  const cancelRefactorBtn = document.getElementById("cancel-refactor")
  const refactorImprovements = document.getElementById("refactor-improvements")

  // Sample code buttons
  const samplePythonBtn = document.getElementById("sample-python")
  const sampleJsBtn = document.getElementById("sample-js")
  const sampleJavaBtn = document.getElementById("sample-java")
  const sampleCBtn = document.getElementById("sample-c")

  // Error modal elements
  const errorModal = document.getElementById("error-modal")
  const errorMessage = document.getElementById("error-message")
  const closeErrorBtn = document.getElementById("close-error-btn")
  const closeErrorBtnBottom = document.getElementById("close-error-btn-bottom")

  // Current language and analysis results
  let currentLanguage = "python"
  let currentAnalysisResults = null

  // Close error modal
  if (closeErrorBtn) {
    closeErrorBtn.addEventListener("click", () => {
      errorModal.classList.add("hidden")
    })
  }

  if (closeErrorBtnBottom) {
    closeErrorBtnBottom.addEventListener("click", () => {
      errorModal.classList.add("hidden")
    })
  }

  // Show error message in custom modal
  function showError(message) {
    errorMessage.textContent = message
    errorModal.classList.remove("hidden")
  }

  // Update editor mode when language changes
  languageSelect.addEventListener("change", function () {
    const language = this.value
    if (language === "auto") return

    currentLanguage = language
    const modeMap = {
      python: "python",
      javascript: "javascript",
      java: "text/x-java",
      c: "text/x-csrc",
    }

    editor.setOption("mode", modeMap[language] || "python")
  })

  // Analyze button click handler
  analyzeBtn.addEventListener("click", () => {
    const code = editor.getValue()
    if (!code.trim()) {
      showError("Please enter some code to analyze.")
      return
    }

    analyzeCode(code, languageSelect.value)
  })

  // Refactor button click handler
  refactorBtn.addEventListener("click", () => {
    const code = editor.getValue()
    if (!code.trim()) {
      showError("Please enter some code to refactor.")
      return
    }

    refactorCode(code, currentLanguage)
  })

  // Close refactor modal
  closeRefactorModalBtn.addEventListener("click", () => {
    refactorModal.classList.add("hidden")
  })

  // Cancel refactor
  cancelRefactorBtn.addEventListener("click", () => {
    refactorModal.classList.add("hidden")
  })

  // Accept refactored code
  acceptRefactorBtn.addEventListener("click", () => {
    const refactoredCode = refactoredEditor.getValue()
    editor.setValue(refactoredCode)
    refactorModal.classList.add("hidden")

    // Re-analyze the refactored code
    analyzeCode(refactoredCode, currentLanguage)
  })

  // Sample code buttons
  samplePythonBtn.addEventListener("click", () => {
    editor.setValue(window.getSampleCode("python"))
    languageSelect.value = "python"
    currentLanguage = "python"
    editor.setOption("mode", "python")
  })

  sampleJsBtn.addEventListener("click", () => {
    editor.setValue(window.getSampleCode("javascript"))
    languageSelect.value = "javascript"
    currentLanguage = "javascript"
    editor.setOption("mode", "javascript")
  })

  sampleJavaBtn.addEventListener("click", () => {
    editor.setValue(window.getSampleCode("java"))
    languageSelect.value = "java"
    currentLanguage = "java"
    editor.setOption("mode", "text/x-java")
  })

  sampleCBtn.addEventListener("click", () => {
    editor.setValue(window.getSampleCode("c"))
    languageSelect.value = "c"
    currentLanguage = "c"
    editor.setOption("mode", "text/x-csrc")
  })

  // Function to analyze code
  async function analyzeCode(code, language) {
    loadingMessage.textContent = "Analyzing code..."
    loadingOverlay.classList.remove("hidden")

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, language }),
      })

      const data = await response.json()

      if (response.ok) {
        currentAnalysisResults = data
        displayResults(data)

        // Update the language dropdown if auto-detect was used
        if (language === "auto" && data.native_analysis && data.native_analysis.language) {
          languageSelect.value = data.native_analysis.language
          currentLanguage = data.native_analysis.language
        }
      } else {
        showError(`Error: ${data.error || "Unknown error occurred"}`)
      }
    } catch (error) {
      console.error("Error:", error)
      showError("An error occurred while analyzing the code. Please try again.")
    } finally {
      loadingOverlay.classList.add("hidden")
    }
  }

  // Function to refactor code
  async function refactorCode(code, language) {
    loadingMessage.textContent = "Refactoring code..."
    loadingOverlay.classList.remove("hidden")

    try {
      const response = await fetch("/api/refactor", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, language }),
      })

      const data = await response.json()

      if (response.ok) {
        displayRefactoredCode(data)
      } else {
        showError(`Error: ${data.error || "Unknown error occurred"}`)
      }
    } catch (error) {
      console.error("Error:", error)
      showError("An error occurred while refactoring the code. Please try again.")
    } finally {
      loadingOverlay.classList.add("hidden")
    }
  }

  // Function to display results
  function displayResults(data) {
    // Hide placeholder, show results
    resultsPlaceholder.classList.add("hidden")
    resultsContainer.classList.remove("hidden")

    // Clear previous results
    metricsGrid.innerHTML = ""
    complexityTable.innerHTML = ""
    aiContent.innerHTML = ""

    const nativeAnalysis = data.native_analysis
    const aiInsights = data.ai_insights

    // Display metrics
    const metrics = [
      { name: "Language", value: nativeAnalysis.language, icon: "fa-code" },
      { name: "Functions", value: nativeAnalysis.functions, icon: "fa-puzzle-piece" },
      { name: "Lines of Code", value: nativeAnalysis.loc, icon: "fa-file-lines" },
      {
        name: "Time Complexity",
        value: formatComplexity(nativeAnalysis.time_complexity),
        icon: "fa-clock",
        complexity: getComplexityLevel(nativeAnalysis.time_complexity),
      },
      {
        name: "Space Complexity",
        value: formatComplexity(nativeAnalysis.space_complexity),
        icon: "fa-memory",
        complexity: getComplexityLevel(nativeAnalysis.space_complexity),
      },
    ]

    metrics.forEach((metric) => {
      const metricCard = document.createElement("div")
      metricCard.className = "metric-card"

      // Add complexity-specific class for time and space complexity
      if (metric.complexity) {
        metricCard.classList.add(`complexity-${metric.complexity}`)
      }

      metricCard.innerHTML = `
        <div class="metric-name">
          <i class="fas ${metric.icon}"></i> ${metric.name}
        </div>
        <div class="metric-value">${metric.value}</div>
      `
      metricsGrid.appendChild(metricCard)
    })

    // Display function complexity table
    if (nativeAnalysis.functions && nativeAnalysis.functions.length > 0) {
      const tableHTML = createFunctionTable(nativeAnalysis.functions)
      complexityTable.innerHTML = tableHTML
    } else {
      complexityTable.innerHTML = "<p>Detailed function complexity analysis not available for this language.</p>"
    }

    // Display AI insights
    aiContent.innerHTML = formatAIInsights(aiInsights)
  }

  // Helper function to get complexity level
  function getComplexityLevel(value) {
    if (typeof value !== "number") return null
    if (value < 10) return "low"
    if (value < 20) return "medium"
    return "high"
  }

  // Function to display refactored code
  function displayRefactoredCode(data) {
    // Set the refactored code in the editor
    refactoredEditor.setValue(data.refactored_code)

    // Update the mode based on current language
    const modeMap = {
      python: "python",
      javascript: "javascript",
      java: "text/x-java",
      c: "text/x-csrc",
    }
    refactoredEditor.setOption("mode", modeMap[currentLanguage] || "python")

    // Display improvements
    refactorImprovements.innerHTML = formatImprovements(data.improvements)

    // Show the modal
    refactorModal.classList.remove("hidden")
  }

  // Helper function to format improvements
  function formatImprovements(improvements) {
    if (!improvements || improvements.length === 0) {
      return "<p>No specific improvements identified.</p>"
    }

    return `
      <ul class="improvements-list">
        ${improvements.map((improvement) => `<li>${improvement}</li>`).join("")}
      </ul>
    `
  }

  // Helper function to format complexity
  function formatComplexity(value) {
    if (typeof value !== "number") return value

    let level = ""
    if (value < 10) {
      level = '<span class="complexity-level level-low">Low</span>'
    } else if (value < 20) {
      level = '<span class="complexity-level level-medium">Medium</span>'
    } else {
      level = '<span class="complexity-level level-high">High</span>'
    }

    return `${value} ${level}`
  }

  // Helper function to create function complexity table
  function createFunctionTable(functions) {
    if (!functions || functions.length === 0) {
      return "<p>No function data available.</p>"
    }

    let html = `
      <table class="complexity-table">
        <thead>
          <tr>
            <th>Function</th>
            <th>Complexity</th>
            <th>LOC</th>
            <th>Nesting</th>
          </tr>
        </thead>
        <tbody>
    `

    functions.forEach((func) => {
      const complexityClass = `level-${func.complexity_level || "low"}`

      html += `
        <tr>
          <td>${func.name}</td>
          <td><span class="complexity-level ${complexityClass}">${func.complexity}</span></td>
          <td>${func.loc}</td>
          <td>${func.nesting}</td>
        </tr>
      `
    })

    html += `
        </tbody>
      </table>
    `

    return html
  }

  // Helper function to format AI insights
  function formatAIInsights(insights) {
    if (!insights) return "<p>AI insights not available.</p>"

    // Convert markdown-like formatting to HTML
    const html = insights
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
      .replace(/\n/g, "<br>")

    return html
  }
})
