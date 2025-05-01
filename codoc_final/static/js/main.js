document.addEventListener("DOMContentLoaded", () => {
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
  const refactorModal = document.getElementById("refactor-modal")
  const closeRefactorModalBtn = document.getElementById("close-refactor-modal")
  const acceptRefactorBtn = document.getElementById("accept-refactor")
  const cancelRefactorBtn = document.getElementById("cancel-refactor")
  const refactorImprovements = document.getElementById("refactor-improvements")

  // Sample code buttons
  const samplePythonBtn = document.getElementById("sample-python")
  const sampleJsBtn = document.getElementById("sample-js")
  const sampleJavaBtn = document.getElementById("sample-java")
  const sampleCBtn = document.getElementById("sample-c")

  // Burger menu elements
  const burgerBtn = document.getElementById("burger-btn")
  const menuDropdown = document.getElementById("menu-dropdown")
  const menuItems = document.querySelectorAll(".menu-item")

  // Page elements
  const analyzerPage = document.getElementById("analyzer-page")
  const modulesPage = document.getElementById("modules-page")
  const aboutPage = document.getElementById("about-page")

  // Current language and analysis results
  let currentLanguage = "python"
  let currentAnalysisResults = null
  let currentPage = "analyzer"

  // Toggle burger menu
  burgerBtn.addEventListener("click", () => {
    menuDropdown.classList.toggle("hidden")
  })

  // Close menu when clicking outside
  document.addEventListener("click", (event) => {
    if (!burgerBtn.contains(event.target) && !menuDropdown.contains(event.target)) {
      menuDropdown.classList.add("hidden")
    }
  })

  // Handle menu item clicks
  menuItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault()
      const page = item.getAttribute("data-page")
      navigateToPage(page)
      menuDropdown.classList.add("hidden")
    })
  })

  // Navigation function
  function navigateToPage(page) {
    // Hide all pages
    analyzerPage.classList.add("hidden")
    modulesPage.classList.add("hidden")
    aboutPage.classList.add("hidden")

    // Remove active class from all menu items
    menuItems.forEach((item) => {
      item.classList.remove("active")
    })

    // Show selected page and mark menu item as active
    if (page === "analyzer") {
      analyzerPage.classList.remove("hidden")
      document.querySelector('[data-page="analyzer"]').classList.add("active")
    } else if (page === "modules") {
      modulesPage.classList.remove("hidden")
      document.querySelector('[data-page="modules"]').classList.add("active")
    } else if (page === "about") {
      aboutPage.classList.remove("hidden")
      document.querySelector('[data-page="about"]').classList.add("active")
    }

    currentPage = page
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
      alert("Please enter some code to analyze.")
      return
    }

    analyzeCode(code, languageSelect.value)
  })

  // Refactor button click handler
  refactorBtn.addEventListener("click", () => {
    const code = editor.getValue()
    if (!code.trim()) {
      alert("Please enter some code to refactor.")
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
    editor.setValue(getSampleCode("python"))
    languageSelect.value = "python"
    currentLanguage = "python"
    editor.setOption("mode", "python")
  })

  sampleJsBtn.addEventListener("click", () => {
    editor.setValue(getSampleCode("javascript"))
    languageSelect.value = "javascript"
    currentLanguage = "javascript"
    editor.setOption("mode", "javascript")
  })

  sampleJavaBtn.addEventListener("click", () => {
    editor.setValue(getSampleCode("java"))
    languageSelect.value = "java"
    currentLanguage = "java"
    editor.setOption("mode", "text/x-java")
  })

  sampleCBtn.addEventListener("click", () => {
    editor.setValue(getSampleCode("c"))
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
      } else {
        alert(`Error: ${data.error || "Unknown error occurred"}`)
      }
    } catch (error) {
      console.error("Error:", error)
      alert("An error occurred while analyzing the code. Please try again.")
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
        alert(`Error: ${data.error || "Unknown error occurred"}`)
      }
    } catch (error) {
      console.error("Error:", error)
      alert("An error occurred while refactoring the code. Please try again.")
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
      { name: "Time Complexity", value: formatComplexity(nativeAnalysis.time_complexity), icon: "fa-clock" },
      { name: "Space Complexity", value: formatComplexity(nativeAnalysis.space_complexity), icon: "fa-memory" },
    ]

    metrics.forEach((metric) => {
      const metricCard = document.createElement("div")
      metricCard.className = "metric-card"
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

  // Sample code for each language
  function getSampleCode(language) {
    const samples = {
      python: `def fibonacci(n):
    """Return the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def bubble_sort(arr):
    """Sort an array using bubble sort algorithm."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Test the functions
print(fibonacci(10))  # Should print 55
print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))`,

      javascript: `function fibonacci(n) {
    // Return the nth Fibonacci number
    if (n <= 0) return 0;
    if (n === 1) return 1;
    
    let a = 0, b = 1;
    for (let i = 2; i <= n; i++) {
        const temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}

function bubbleSort(arr) {
    // Sort an array using bubble sort algorithm
    const n = arr.length;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                // Swap elements
                [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
            }
        }
    }
    return arr;
}

// Test the functions
console.log(fibonacci(10)); // Should print 55
console.log(bubbleSort([64, 34, 25, 12, 22, 11, 90]));`,

      java: `public class Algorithms {
    public static int fibonacci(int n) {
        // Return the nth Fibonacci number
        if (n <= 0) return 0;
        if (n == 1) return 1;
        
        int a = 0, b = 1;
        for (int i = 2; i <= n; i++) {
            int temp = a + b;
            a = b;
            b = temp;
        }
        return b;
    }
    
    public static int[] bubbleSort(int[] arr) {
        // Sort an array using bubble sort algorithm
        int n = arr.length;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    // Swap elements
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        return arr;
    }
    
    public static void main(String[] args) {
        // Test the functions
        System.out.println(fibonacci(10)); // Should print 55
        
        int[] array = {64, 34, 25, 12, 22, 11, 90};
        bubbleSort(array);
        
        for (int num : array) {
            System.out.print(num + " ");
        }
    }
}`,

      c: `#include <stdio.h>

int fibonacci(int n) {
    /* Return the nth Fibonacci number */
    if (n <= 0) return 0;
    if (n == 1) return 1;
    
    int a = 0, b = 1, temp;
    for (int i = 2; i <= n; i++) {
        temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}

void bubbleSort(int arr[], int n) {
    /* Sort an array using bubble sort algorithm */
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                // Swap elements
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    // Test the functions
    printf("Fibonacci(10) = %d\\n", fibonacci(10)); // Should print 55
    
    int array[] = {64, 34, 25, 12, 22, 11, 90};
    int n = sizeof(array) / sizeof(array[0]);
    
    bubbleSort(array, n);
    
    printf("Sorted array: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", array[i]);
    }
    
    return 0;
}`,
    }

    return samples[language] || ""
  }

  // Initialize the app with the analyzer page
  navigateToPage("analyzer")
})
