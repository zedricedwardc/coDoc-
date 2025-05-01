// Sample code for each language
function getSampleCode(language) {
    const samples = {
      python: `#!/usr/bin/env python3
  # Python implementation of Fibonacci and Bubble Sort algorithms
  
  def fibonacci(n):
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
  if __name__ == "__main__":
      print(fibonacci(10))  # Should print 55
      print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))`,
  
      javascript: `// JavaScript implementation of Fibonacci and Bubble Sort algorithms
  
  function fibonacci(n) {
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
  
      java: `// Java implementation of Fibonacci and Bubble Sort algorithms
  
  public class Algorithms {
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
  
      c: `// C implementation of Fibonacci and Bubble Sort algorithms
  
  #include <stdio.h>
  
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
  
  // Export the function for use in other files
  window.getSampleCode = getSampleCode
  