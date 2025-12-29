"""
Terraform HCL Parser

Provides utilities for reading and parsing Terraform module configurations.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class TerraformResource:
    """Represents a Terraform resource"""

    def __init__(
        self,
        resource_type: str,
        resource_name: str,
        attributes: Dict[str, Any],
        file_path: str,
        line_number: int,
    ):
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.attributes = attributes
        self.file_path = file_path
        self.line_number = line_number

    @property
    def full_name(self) -> str:
        """Get full resource name (type.name)"""
        return f"{self.resource_type}.{self.resource_name}"

    def has_attribute(self, attr_name: str) -> bool:
        """Check if resource has a specific attribute"""
        return attr_name in self.attributes

    def get_attribute(self, attr_name: str, default: Any = None) -> Any:
        """Get attribute value with optional default"""
        return self.attributes.get(attr_name, default)


class TerraformModule:
    """Represents a Terraform module"""

    def __init__(self, module_path: str):
        self.module_path = Path(module_path)
        self.resources: List[TerraformResource] = []
        self.variables: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self.locals: Dict[str, Any] = {}

    def get_resources_by_type(self, resource_type: str) -> List[TerraformResource]:
        """Get all resources of a specific type"""
        return [r for r in self.resources if r.resource_type == resource_type]

    def get_resource(
        self, resource_type: str, resource_name: str
    ) -> Optional[TerraformResource]:
        """Get a specific resource by type and name"""
        for resource in self.resources:
            if (
                resource.resource_type == resource_type
                and resource.resource_name == resource_name
            ):
                return resource
        return None

    def has_resource_type(self, resource_type: str) -> bool:
        """Check if module contains any resources of given type"""
        return len(self.get_resources_by_type(resource_type)) > 0


class TerraformParser:
    """Parser for Terraform HCL files"""

    def __init__(self):
        pass

    def parse_module(self, module_path: str) -> TerraformModule:
        """
        Parse a Terraform module directory

        Args:
            module_path: Path to the module directory

        Returns:
            TerraformModule object with parsed resources
        """
        module = TerraformModule(module_path)
        module_dir = Path(module_path)

        if not module_dir.exists():
            raise FileNotFoundError(f"Module directory not found: {module_path}")

        # Parse all .tf files in the module
        for tf_file in module_dir.glob("*.tf"):
            self._parse_file(tf_file, module)

        return module

    def _parse_file(self, file_path: Path, module: TerraformModule) -> None:
        """
        Parse a single Terraform file

        Args:
            file_path: Path to the .tf file
            module: TerraformModule to add parsed resources to
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse resources
            resources = self._extract_resources(content, str(file_path))
            module.resources.extend(resources)

            # Parse variables
            variables = self._extract_variables(content)
            module.variables.update(variables)

            # Parse outputs
            outputs = self._extract_outputs(content)
            module.outputs.update(outputs)

            # Parse locals
            locals_dict = self._extract_locals(content)
            module.locals.update(locals_dict)

        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")

    def _extract_resources(
        self, content: str, file_path: str
    ) -> List[TerraformResource]:
        """
        Extract resource blocks from Terraform content

        This is a simplified parser that extracts basic resource information.
        For production use, consider using python-hcl2 or similar library.
        """
        resources = []

        # Pattern to match resource blocks
        # resource "type" "name" {
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'

        matches = re.finditer(resource_pattern, content)

        for match in matches:
            resource_type = match.group(1)
            resource_name = match.group(2)
            start_pos = match.end()

            # Find the matching closing brace
            block_content = self._extract_block_content(content, start_pos)

            # Extract attributes from block content
            attributes = self._parse_attributes(block_content)

            # Calculate line number
            line_number = content[: match.start()].count("\n") + 1

            resource = TerraformResource(
                resource_type=resource_type,
                resource_name=resource_name,
                attributes=attributes,
                file_path=file_path,
                line_number=line_number,
            )

            resources.append(resource)

        return resources

    def _extract_block_content(self, content: str, start_pos: int) -> str:
        """
        Extract content between matching braces

        Args:
            content: Full file content
            start_pos: Position after opening brace

        Returns:
            Content between braces
        """
        brace_count = 1
        pos = start_pos

        while pos < len(content) and brace_count > 0:
            if content[pos] == "{":
                brace_count += 1
            elif content[pos] == "}":
                brace_count -= 1
            pos += 1

        return content[start_pos : pos - 1]

    def _parse_attributes(self, block_content: str) -> Dict[str, Any]:
        """
        Parse attributes from a resource block

        This is a simplified parser. For production, use python-hcl2.
        """
        attributes = {}

        # Pattern for simple key = value attributes
        attr_pattern = r"^\s*([a-z_][a-z0-9_]*)\s*=\s*(.+?)(?=\n\s*[a-z_]|\n\s*\}|\Z)"

        matches = re.finditer(attr_pattern, block_content, re.MULTILINE | re.DOTALL)

        for match in matches:
            key = match.group(1)
            value = match.group(2).strip()

            # Store raw value (simplified - doesn't parse complex types)
            attributes[key] = value

        return attributes

    def _extract_variables(self, content: str) -> Dict[str, Any]:
        """Extract variable definitions"""
        variables = {}

        var_pattern = r'variable\s+"([^"]+)"\s*\{'
        matches = re.finditer(var_pattern, content)

        for match in matches:
            var_name = match.group(1)
            start_pos = match.end()
            block_content = self._extract_block_content(content, start_pos)

            # Extract variable properties
            var_props = self._parse_attributes(block_content)
            variables[var_name] = var_props

        return variables

    def _extract_outputs(self, content: str) -> Dict[str, Any]:
        """Extract output definitions"""
        outputs = {}

        output_pattern = r'output\s+"([^"]+)"\s*\{'
        matches = re.finditer(output_pattern, content)

        for match in matches:
            output_name = match.group(1)
            start_pos = match.end()
            block_content = self._extract_block_content(content, start_pos)

            # Extract output properties
            output_props = self._parse_attributes(block_content)
            outputs[output_name] = output_props

        return outputs

    def _extract_locals(self, content: str) -> Dict[str, Any]:
        """Extract locals definitions"""
        locals_dict = {}

        locals_pattern = r"locals\s*\{"
        matches = re.finditer(locals_pattern, content)

        for match in matches:
            start_pos = match.end()
            block_content = self._extract_block_content(content, start_pos)

            # Extract local values
            local_values = self._parse_attributes(block_content)
            locals_dict.update(local_values)

        return locals_dict

    def read_file_content(self, file_path: str) -> str:
        """
        Read raw content of a Terraform file

        Args:
            file_path: Path to the file

        Returns:
            File content as string
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_resource_snippet(
        self, file_path: str, resource_type: str, resource_name: str
    ) -> Optional[str]:
        """
        Extract the code snippet for a specific resource

        Args:
            file_path: Path to the Terraform file
            resource_type: Resource type
            resource_name: Resource name

        Returns:
            Code snippet or None if not found
        """
        content = self.read_file_content(file_path)

        # Find the resource block
        pattern = rf'resource\s+"{re.escape(resource_type)}"\s+"{re.escape(resource_name)}"\s*\{{'
        match = re.search(pattern, content)

        if not match:
            return None

        start_pos = match.start()
        block_start = match.end()
        block_content = self._extract_block_content(content, block_start)

        # Return the full resource block
        return content[start_pos : block_start + len(block_content) + 1]


def parse_terraform_module(module_path: str) -> TerraformModule:
    """
    Convenience function to parse a Terraform module

    Args:
        module_path: Path to the module directory

    Returns:
        Parsed TerraformModule
    """
    parser = TerraformParser()
    return parser.parse_module(module_path)
