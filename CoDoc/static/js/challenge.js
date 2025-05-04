document.addEventListener("DOMContentLoaded", () => {
  // Initialize CodeMirror for challenge editor with placeholder
  const editor = CodeMirror.fromTextArea(document.getElementById("challenge-editor"), {
    mode: "python",
    theme: "dracula",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    autoCloseBrackets: true,
    matchBrackets: true,
    lineWrapping: true,
    placeholder: "// Click here and start coding your solution...",
  })

  // Set initial height
  editor.setSize(null, "100%")

  // Elements
  const languageSelect = document.getElementById("challenge-language")
  const submitBtn = document.getElementById("challenge-submit")
  const challengeItems = document.getElementById("challenge-items")
  const editorTitle = document.getElementById("editor-title")
  const challengeStatus = document.getElementById("challenge-status")
  const loadingOverlay = document.getElementById("loading-overlay")
  const loadingMessage = document.getElementById("loading-message")

  // Result modal elements
  const resultModal = document.getElementById("challenge-result-modal")
  const closeResultModalBtn = document.getElementById("close-result-modal")
  const closeResultBtn = document.getElementById("close-result-btn")
  const challengeGrade = document.getElementById("challenge-grade")
  const challengeScore = document.getElementById("challenge-score")
  const timeComplexityItem = document.getElementById("time-complexity-item")
  const spaceComplexityItem = document.getElementById("space-complexity-item")
  const timeComplexityValue = document.getElementById("time-complexity-value")
  const spaceComplexityValue = document.getElementById("space-complexity-value")
  const challengeStrengths = document.getElementById("challenge-strengths")
  const challengeImprovements = document.getElementById("challenge-improvements")

  // Error modal elements
  const errorModal = document.getElementById("error-modal")
  const errorMessage = document.getElementById("error-message")
  const closeErrorBtn = document.getElementById("close-error-btn")
  const closeErrorBtnBottom = document.getElementById("close-error-btn-bottom")

  // Current challenge
  let currentChallengeId = null

  // Challenge data
  const challenges = {
    1: {
      title: "Two Sum",
      difficulty: "easy",
      description: `
        <h2>Two Sum</h2>
        <p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return the indices of the two numbers such that they add up to <code>target</code>.</p>
        
        <p>You may assume that each input would have <strong>exactly one solution</strong>, and you may not use the same element twice.</p>
        
        <h3>Examples</h3>
        <pre><code>Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].</code></pre>

        <pre><code>Input: nums = [3, 2, 4], target = 6
Output: [1, 2]</code></pre>

        <h3>Constraints</h3>
        <ul>
          <li>2 ≤ nums.length ≤ 10<sup>4</sup></li>
          <li>-10<sup>9</sup> ≤ nums[i] ≤ 10<sup>9</sup></li>
          <li>-10<sup>9</sup> ≤ target ≤ 10<sup>9</sup></li>
          <li>Only one valid answer exists.</li>
        </ul>
        
        <h3>Challenge</h3>
        <p>Can you come up with an algorithm that is less than O(n²) time complexity?</p>
        
        <h3>Function Signature</h3>
        <pre><code>def two_sum(nums, target):
    # Your code here
    pass</code></pre>
      `,
      placeholder: {
        python: `# Write your solution here
def two_sum(nums, target):
    # Your code here
    pass`,
        javascript: `// Write your solution here
/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
function twoSum(nums, target) {
    // Your code here
};`,
      },
    },
    2: {
      title: "Longest Palindromic Substring",
      difficulty: "medium",
      description: `
        <h2>Longest Palindromic Substring</h2>
        <p>Given a string <code>s</code>, return the longest palindromic substring in <code>s</code>.</p>
        
        <p>A palindrome is a string that reads the same backward as forward, such as "madam" or "racecar".</p>
        
        <h3>Examples</h3>
        <pre><code>Input: s = "babad"
Output: "bab" or "aba" (both are valid)</code></pre>

        <pre><code>Input: s = "cbbd"
Output: "bb"</code></pre>

        <h3>Constraints</h3>
        <ul>
          <li>1 ≤ s.length ≤ 1000</li>
          <li>s consists only of lowercase English letters.</li>
        </ul>
        
        <h3>Challenge</h3>
        <p>Can you find a solution with O(n²) time complexity or better?</p>
        
        <h3>Function Signature</h3>
        <pre><code>def longest_palindrome(s):
    # Your code here
    pass</code></pre>
      `,
      placeholder: {
        python: `# Write your solution here
def longest_palindrome(s):
    # Your code here
    pass`,
        javascript: `// Write your solution here
/**
 * @param {string} s
 * @return {string}
 */
function longestPalindrome(s) {
    // Your code here
};`,
      },
    },
    3: {
      title: "Binary Tree Maximum Path Sum",
      difficulty: "hard",
      description: `
        <h2>Binary Tree Maximum Path Sum</h2>
        <p>A <strong>path</strong> in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence <strong>at most once</strong>. Note that the path does not need to pass through the root.</p>
        
        <p>The <strong>path sum</strong> of a path is the sum of the node's values in the path.</p>
        
        <p>Given the <code>root</code> of a binary tree, return the maximum path sum of any non-empty path.</p>
        
        <h3>Examples</h3>
        <pre><code>Input: root = [1, 2, 3]
Output: 6
Explanation: The optimal path is 2 -> 1 -> 3 with a path sum of 2 + 1 + 3 = 6.</code></pre>

        <pre><code>Input: root = [-10, 9, 20, null, null, 15, 7]
Output: 42
Explanation: The optimal path is 15 -> 20 -> 7 with a path sum of 15 + 20 + 7 = 42.</code></pre>

        <h3>Constraints</h3>
        <ul>
          <li>The number of nodes in the tree is in the range [1, 3 * 10<sup>4</sup>].</li>
          <li>-1000 ≤ Node.val ≤ 1000</li>
        </ul>
        
        <h3>Challenge</h3>
        <p>Can you find a solution with O(n) time complexity?</p>
        
        <h3>Function Signature</h3>
        <pre><code>def max_path_sum(root):
    # Your code here
    pass</code></pre>
      `,
      placeholder: {
        python: `# Write your solution here
# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_path_sum(root):
    # Your code here
    pass`,
        javascript: `// Write your solution here
/**
 * Definition for a binary tree node.
 * function TreeNode(val, left, right) {
 *     this.val = (val===undefined ? 0 : val)
 *     this.left = (left===undefined ? null : left)
 *     this.right = (right===undefined ? null : right)
 * }
 */
/**
 * @param {TreeNode} root
 * @return {number}
 */
function maxPathSum(root) {
    // Your code here
};`,
      },
    },
  }

  // Populate challenge list
  populateChallengeList()

  // Update editor mode when language changes
  languageSelect.addEventListener("change", function () {
    const language = this.value
    const modeMap = {
      python: "python",
      javascript: "javascript",
    }
    editor.setOption("mode", modeMap[language] || "python")

    // Update placeholder based on selected language if a challenge is selected
    if (currentChallengeId) {
      const placeholder = challenges[currentChallengeId].placeholder[language]
      if (placeholder) {
        // Clear editor and set placeholder
        editor.setValue("")
        editor.setOption("placeholder", placeholder)
      }
    }
  })

  // Submit button click handler
  submitBtn.addEventListener("click", () => {
    const code = editor.getValue()
    if (!code.trim()) {
      showError("Please write some code before submitting.")
      return
    }

    if (!currentChallengeId) {
      showError("Please select a challenge first.")
      return
    }

    submitSolution(code, currentChallengeId, languageSelect.value)
  })

  // Close result modal buttons
  if (closeResultModalBtn) {
    closeResultModalBtn.addEventListener("click", () => {
      resultModal.classList.add("hidden")
    })
  }

  if (closeResultBtn) {
    closeResultBtn.addEventListener("click", () => {
      resultModal.classList.add("hidden")
    })
  }

  // Close error modal buttons
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

  // Function to show error in modal
  function showError(message) {
    errorMessage.textContent = message
    errorModal.classList.remove("hidden")
  }

  // Function to populate challenge list
  function populateChallengeList() {
    challengeItems.innerHTML = ""

    Object.keys(challenges).forEach((id) => {
      const challenge = challenges[id]
      const item = document.createElement("div")

      item.className = "challenge-item"
      item.setAttribute("data-challenge", id)

      // Create header and content sections
      const header = document.createElement("div")
      header.className = "challenge-item-header"
      header.innerHTML = `
        <div class="challenge-item-title">${challenge.title}</div>
        <div class="challenge-item-difficulty">
          <span class="complexity-level level-${getDifficultyClass(challenge.difficulty)}">
            ${challenge.difficulty.charAt(0).toUpperCase() + challenge.difficulty.slice(1)}
          </span>
        </div>
      `

      const content = document.createElement("div")
      content.className = "challenge-item-content"
      content.innerHTML = challenge.description

      // Add click event to header
      header.addEventListener("click", () => {
        // Toggle active state for this item
        const isActive = item.classList.contains("active")

        // Close all other items
        document.querySelectorAll(".challenge-item").forEach((el) => {
          el.classList.remove("active")
        })

        // If this wasn't active, make it active
        if (!isActive) {
          item.classList.add("active")
          loadChallenge(id)
        } else {
          // If it was active and we clicked it again, just close it
          currentChallengeId = null
          submitBtn.disabled = true
          challengeStatus.textContent = "Select a challenge to begin"
          editorTitle.textContent = "Code Solution"
          editor.setValue("")
          editor.setOption("placeholder", "// Click here and start coding your solution...")
        }
      })

      // Append header and content to item
      item.appendChild(header)
      item.appendChild(content)
      challengeItems.appendChild(item)
    })
  }

  // Function to load a challenge
  function loadChallenge(challengeId) {
    currentChallengeId = challengeId
    const challenge = challenges[challengeId]

    // Update editor title
    editorTitle.textContent = `Solution: ${challenge.title}`

    // Update placeholder based on selected language
    const language = languageSelect.value
    const placeholder = challenge.placeholder[language]
    if (placeholder) {
      // Clear editor and set placeholder
      editor.setValue("")
      editor.setOption("placeholder", placeholder)
    }

    // Enable submit button
    submitBtn.disabled = false

    // Reset status
    challengeStatus.textContent = "Ready to code!"
  }

  // Function to submit a solution
  async function submitSolution(code, challengeId, language) {
    loadingMessage.textContent = "Evaluating your solution..."
    loadingOverlay.classList.remove("hidden")

    try {
      const response = await fetch("/api/challenge/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, challenge_id: challengeId, language }),
      })

      const data = await response.json()

      if (response.ok) {
        displayResult(data)
      } else {
        showError(data.error || "Unknown error occurred")
      }
    } catch (error) {
      console.error("Error:", error)
      showError("An error occurred while evaluating your solution. Please try again.")
    } finally {
      loadingOverlay.classList.add("hidden")
    }
  }

  // Function to display result
  function displayResult(result) {
    // Calculate grade based on score
    let grade = "F"
    if (result.score >= 90) grade = "A"
    else if (result.score >= 80) grade = "B"
    else if (result.score >= 70) grade = "C"
    else if (result.score >= 60) grade = "D"

    // Update grade and score
    challengeGrade.textContent = grade
    challengeScore.textContent = result.score

    // Update complexity values
    timeComplexityValue.textContent = `O(${getComplexityNotation(result.time_complexity)})`
    spaceComplexityValue.textContent = `O(${getComplexityNotation(result.space_complexity)})`

    // Add complexity classes
    const timeComplexityClass = getComplexityClass(result.time_complexity)
    const spaceComplexityClass = getComplexityClass(result.space_complexity)

    timeComplexityItem.className = `complexity-item ${timeComplexityClass}`
    spaceComplexityItem.className = `complexity-item ${spaceComplexityClass}`

    // Update strengths and improvements
    challengeStrengths.innerHTML = ""
    challengeImprovements.innerHTML = ""

    // Add strengths based on complexity
    const strengths = []
    if (result.time_complexity < 10) {
      strengths.push("Excellent time complexity - your algorithm is very efficient!")
    }
    if (result.space_complexity < 10) {
      strengths.push("Great space efficiency - minimal memory usage!")
    }
    if (result.score >= 80) {
      strengths.push("Well-structured solution with good overall performance.")
    }

    // If no specific strengths, add a generic one
    if (strengths.length === 0) {
      strengths.push("Your solution correctly addresses the problem requirements.")
    }

    // Add improvements based on complexity
    const improvements = []
    if (result.time_complexity >= 10) {
      improvements.push("Consider optimizing time complexity - look for more efficient algorithms.")
    }
    if (result.space_complexity >= 10) {
      improvements.push("Try to reduce memory usage by optimizing data structures.")
    }
    if (result.score < 80) {
      improvements.push("Review your algorithm design for better overall efficiency.")
    }

    // If no specific improvements, add a generic one
    if (improvements.length === 0) {
      improvements.push("Your solution is already quite optimized, but you could try to refactor for readability.")
    }

    // Add feedback items to the lists
    strengths.forEach((strength) => {
      const li = document.createElement("li")
      li.textContent = strength
      challengeStrengths.appendChild(li)
    })

    improvements.forEach((improvement) => {
      const li = document.createElement("li")
      li.textContent = improvement
      challengeImprovements.appendChild(li)
    })

    // Show modal
    resultModal.classList.remove("hidden")

    // Update status
    challengeStatus.textContent = `Last score: ${result.score}`
  }

  // Helper function to get complexity class
  function getComplexityClass(value) {
    if (typeof value !== "number") return ""
    if (value < 10) return "low"
    if (value < 20) return "medium"
    return "high"
  }

  // Helper function to get difficulty class
  function getDifficultyClass(difficulty) {
    switch (difficulty.toLowerCase()) {
      case "easy":
        return "low"
      case "medium":
        return "medium"
      case "hard":
        return "high"
      default:
        return "medium"
    }
  }

  // Helper function to convert complexity value to notation
  function getComplexityNotation(value) {
    if (value <= 1) return "1"
    if (value <= 5) return "log n"
    if (value <= 10) return "n"
    if (value <= 15) return "n log n"
    if (value <= 20) return "n²"
    return "2ⁿ"
  }
})
