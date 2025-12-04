package test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Feature: terraform-modularization, Property 1: Module structure completeness
// Validates: Requirements 1.2
// Property: For any service module (cloudtrail, config, detective, guardduty, securityhub),
// the module directory SHALL contain main.tf, variables.tf, outputs.tf, and README.md files.
func TestDetectiveModuleStructureCompleteness(t *testing.T) {
	t.Parallel()

	modulePath := "../modules/detective"
	requiredFiles := []string{"main.tf", "variables.tf", "outputs.tf", "README.md"}

	for _, file := range requiredFiles {
		filePath := filepath.Join(modulePath, file)
		t.Run("File_"+file+"_exists", func(t *testing.T) {
			_, err := os.Stat(filePath)
			assert.NoError(t, err, "Required file %s should exist in Detective module", file)
		})
	}
}
