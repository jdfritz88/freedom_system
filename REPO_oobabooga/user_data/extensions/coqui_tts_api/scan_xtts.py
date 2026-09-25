"""
XTTS Configuration Diagnostic Tool
This tool identifies configuration mismatches that cause the srcIndex < srcSelectDimSize error.
"""

import torch
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XTTSDiagnostic:
    """
    Comprehensive diagnostic tool for XTTS configuration issues.
    """
    
    def __init__(self, model=None, config=None, tokenizer=None):
        """
        Initialize diagnostic tool.
        
        Args:
            model: Your XTTS model instance
            config: Model configuration object
            tokenizer: Tokenizer instance
        """
        self.model = model
        self.config = config
        self.tokenizer = tokenizer
        self.issues_found = []
        self.recommendations = []
        
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """
        Run comprehensive diagnostic and return detailed report.
        
        Returns:
            Dictionary with diagnostic results and recommendations
        """
        logger.info("Starting XTTS Configuration Diagnostic...")
        
        # Get environment info safely
        try:
            env_info = f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}"
        except:
            env_info = "Environment info unavailable"
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'environment': env_info,
            'model_info': self._diagnose_model_config(),
            'tokenizer_info': self._diagnose_tokenizer(),
            'tensor_compatibility': self._diagnose_tensor_compatibility(),
            'text_processing': self._diagnose_text_processing(),
            'dimension_analysis': self._diagnose_dimension_matching(),
            'issues_found': self.issues_found,
            'recommendations': self.recommendations,
            'severity_score': self._calculate_severity_score()
        }
        
        self._generate_final_recommendations(report)
        return report
    
    def _diagnose_model_config(self) -> Dict[str, Any]:
        """Diagnose model configuration issues."""
        logger.info("Diagnosing model configuration...")
        
        model_info = {
            'model_present': self.model is not None,
            'config_present': self.config is not None,
            'model_type': None,
            'expected_input_shape': None,
            'max_sequence_length': None,
            'vocab_size': None,
            'device': None,
            'dtype': None
        }
        
        if self.model is not None:
            try:
                model_info['model_type'] = type(self.model).__name__
                
                # Safely get device and dtype
                try:
                    first_param = next(self.model.parameters())
                    model_info['device'] = str(first_param.device)
                    model_info['dtype'] = str(first_param.dtype)
                except:
                    model_info['device'] = "Unknown"
                    model_info['dtype'] = "Unknown"
                
                # Try to get model configuration
                if hasattr(self.model, 'config'):
                    config = self.model.config
                    model_info['max_sequence_length'] = getattr(config, 'max_seq_len', None)
                    model_info['vocab_size'] = getattr(config, 'vocab_size', None)
                    model_info['hidden_size'] = getattr(config, 'hidden_size', None)
                    model_info['num_layers'] = getattr(config, 'num_layers', None)
                
                # Check for XTTS-specific attributes
                if hasattr(self.model, 'tts'):
                    model_info['has_tts_module'] = True
                    if hasattr(self.model.tts, 'config'):
                        tts_config = self.model.tts.config
                        model_info['tts_vocab_size'] = getattr(tts_config, 'vocab_size', None)
                        model_info['tts_max_seq_len'] = getattr(tts_config, 'max_seq_len', None)
                
                # Check for common XTTS attributes
                if hasattr(self.model, 'tokenizer'):
                    model_info['has_builtin_tokenizer'] = True
                    self.tokenizer = self.model.tokenizer
                elif hasattr(self.model, 'tts') and hasattr(self.model.tts, 'tokenizer'):
                    model_info['has_tts_tokenizer'] = True
                    self.tokenizer = self.model.tts.tokenizer
                
            except Exception as e:
                self.issues_found.append({
                    'severity': 'high',
                    'category': 'model_config',
                    'message': f"Failed to analyze model configuration: {str(e)}",
                    'traceback': traceback.format_exc()
                })
        
        return model_info
    
    def _diagnose_tokenizer(self) -> Dict[str, Any]:
        """Diagnose tokenizer configuration and compatibility."""
        logger.info("Diagnosing tokenizer configuration...")
        
        tokenizer_info = {
            'tokenizer_present': self.tokenizer is not None,
            'tokenizer_type': None,
            'vocab_size': None,
            'max_length': None,
            'pad_token': None,
            'eos_token': None,
            'unk_token': None,
            'special_tokens': None
        }
        
        if self.tokenizer is not None:
            try:
                tokenizer_info['tokenizer_type'] = type(self.tokenizer).__name__
                
                # Get tokenizer properties safely
                tokenizer_info['vocab_size'] = getattr(self.tokenizer, 'vocab_size', None)
                tokenizer_info['max_length'] = getattr(self.tokenizer, 'model_max_length', None)
                
                # Check special tokens
                special_tokens = {}
                for token_name in ['pad_token', 'eos_token', 'unk_token', 'bos_token']:
                    if hasattr(self.tokenizer, token_name):
                        token = getattr(self.tokenizer, token_name)
                        special_tokens[token_name] = str(token) if token else None
                
                tokenizer_info['special_tokens'] = special_tokens
                
                # Test tokenizer with problematic text
                test_text = "ok.. well im feeling incredibly turned on by this direction"
                try:
                    # Different tokenizers have different methods
                    if hasattr(self.tokenizer, 'encode'):
                        tokens = self.tokenizer.encode(test_text)
                    elif hasattr(self.tokenizer, '__call__'):
                        result = self.tokenizer(test_text)
                        tokens = result.get('input_ids', []) if isinstance(result, dict) else result
                    else:
                        tokens = []
                        
                    tokenizer_info['test_tokenization'] = {
                        'input_text': test_text,
                        'token_count': len(tokens),
                        'tokens': tokens[:20],  # First 20 tokens for inspection
                        'max_token_id': max(tokens) if tokens else None
                    }
                    
                    # Check if max token ID exceeds vocab size
                    if tokenizer_info['vocab_size'] and tokenizer_info['test_tokenization']['max_token_id']:
                        if tokenizer_info['test_tokenization']['max_token_id'] >= tokenizer_info['vocab_size']:
                            self.issues_found.append({
                                'severity': 'critical',
                                'category': 'tokenizer',
                                'message': f"Token ID {tokenizer_info['test_tokenization']['max_token_id']} exceeds vocab size {tokenizer_info['vocab_size']}",
                                'fix': 'Check tokenizer configuration or model vocabulary'
                            })
                
                except Exception as tokenize_error:
                    tokenizer_info['tokenization_error'] = str(tokenize_error)
                    self.issues_found.append({
                        'severity': 'high',
                        'category': 'tokenizer',
                        'message': f"Tokenization failed: {str(tokenize_error)}",
                        'fix': 'Check tokenizer compatibility with input text'
                    })
                
            except Exception as e:
                self.issues_found.append({
                    'severity': 'high',
                    'category': 'tokenizer',
                    'message': f"Failed to analyze tokenizer: {str(e)}",
                    'traceback': traceback.format_exc()
                })
        
        return tokenizer_info
    
    def _diagnose_tensor_compatibility(self) -> Dict[str, Any]:
        """Diagnose tensor compatibility issues."""
        logger.info("Diagnosing tensor compatibility...")
        
        tensor_info = {
            'cuda_available': torch.cuda.is_available(),
            'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
            'current_device': torch.cuda.current_device() if torch.cuda.is_available() else None,
            'memory_info': None,
            'tensor_creation_test': None
        }
        
        if torch.cuda.is_available():
            try:
                # Get memory info
                memory_info = {}
                for i in range(torch.cuda.device_count()):
                    try:
                        device_props = torch.cuda.get_device_properties(i)
                        memory_info[f'device_{i}'] = {
                            'name': device_props.name,
                            'total_memory': device_props.total_memory,
                            'allocated_memory': torch.cuda.memory_allocated(i),
                            'reserved_memory': torch.cuda.memory_reserved(i)
                        }
                    except:
                        memory_info[f'device_{i}'] = {'error': 'Could not get device info'}
                
                tensor_info['memory_info'] = memory_info
                
                # Test tensor creation and indexing
                test_results = self._test_tensor_operations()
                tensor_info['tensor_creation_test'] = test_results
                
            except Exception as e:
                self.issues_found.append({
                    'severity': 'medium',
                    'category': 'tensor_compatibility',
                    'message': f"Failed to analyze tensor compatibility: {str(e)}",
                    'traceback': traceback.format_exc()
                })
        
        return tensor_info
    
    def _test_tensor_operations(self) -> Dict[str, Any]:
        """Test basic tensor operations that might fail."""
        test_results = {
            'basic_tensor_creation': False,
            'indexing_operations': False,
            'attention_mask_test': False,
            'sequence_processing': False,
            'error_details': []
        }
        
        try:
            # Test basic tensor creation
            test_tensor = torch.randn(10, 20).cuda()
            test_results['basic_tensor_creation'] = True
            
            # Test indexing operations (the source of our error)
            indices = torch.tensor([0, 1, 2, 3, 4]).cuda()
            indexed_tensor = test_tensor[indices]
            test_results['indexing_operations'] = True
            
            # Test attention mask creation
            seq_len = 50
            attention_mask = torch.ones(1, seq_len).cuda()
            test_results['attention_mask_test'] = True
            
            # Test sequence processing similar to TTS
            batch_size = 1
            seq_len = 100
            vocab_size = 1000
            
            input_ids = torch.randint(0, vocab_size, (batch_size, seq_len)).cuda()
            attention_mask = torch.ones(batch_size, seq_len).cuda()
            
            # This simulates the operation that's failing
            selected_tokens = input_ids[attention_mask.bool()]
            test_results['sequence_processing'] = True
            
        except Exception as e:
            error_detail = {
                'operation': 'tensor_operations',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            test_results['error_details'].append(error_detail)
            
            self.issues_found.append({
                'severity': 'critical',
                'category': 'tensor_operations',
                'message': f"Tensor operation failed: {str(e)}",
                'traceback': traceback.format_exc(),
                'fix': 'This indicates a fundamental tensor compatibility issue'
            })
        
        return test_results
    
    def _diagnose_text_processing(self) -> Dict[str, Any]:
        """Diagnose text processing pipeline."""
        logger.info("Diagnosing text processing pipeline...")
        
        # Test the exact text that caused the crash
        problematic_text = "ok.. well im feeling incredibly turned on by this direction"
        
        processing_info = {
            'original_text': problematic_text,
            'sentence_splitting': None,
            'tokenization_result': None,
            'tensor_shapes': None,
            'potential_issues': []
        }
        
        try:
            # Test sentence splitting (as shown in your error log)
            # This simulates what XTTS does internally
            sentences = [s.strip() for s in problematic_text.split('.') if s.strip()]
            processing_info['sentence_splitting'] = sentences
            
            if self.tokenizer:
                # Test tokenization of each sentence
                tokenization_results = []
                for sentence in sentences:
                    try:
                        if hasattr(self.tokenizer, 'encode'):
                            tokens = self.tokenizer.encode(sentence)
                        elif hasattr(self.tokenizer, '__call__'):
                            result = self.tokenizer(sentence)
                            tokens = result.get('input_ids', []) if isinstance(result, dict) else result
                        else:
                            tokens = []
                            
                        tokenization_results.append({
                            'sentence': sentence,
                            'tokens': tokens,
                            'token_count': len(tokens)
                        })
                    except Exception as e:
                        tokenization_results.append({
                            'sentence': sentence,
                            'error': str(e),
                            'token_count': 0
                        })
                
                processing_info['tokenization_result'] = tokenization_results
                
                # Check for length mismatches
                token_counts = [r.get('token_count', 0) for r in tokenization_results]
                if len(set(token_counts)) > 1:
                    processing_info['potential_issues'].append({
                        'issue': 'Variable sentence lengths',
                        'details': f"Token counts: {token_counts}",
                        'severity': 'medium'
                    })
                
                # Check for empty tokenization
                if any(count == 0 for count in token_counts):
                    processing_info['potential_issues'].append({
                        'issue': 'Empty tokenization detected',
                        'details': 'Some sentences produced no tokens',
                        'severity': 'high'
                    })
            
        except Exception as e:
            self.issues_found.append({
                'severity': 'high',
                'category': 'text_processing',
                'message': f"Text processing failed: {str(e)}",
                'traceback': traceback.format_exc()
            })
        
        return processing_info
    
    def _diagnose_dimension_matching(self) -> Dict[str, Any]:
        """Diagnose dimension matching issues between components."""
        logger.info("Diagnosing dimension matching...")
        
        dimension_info = {
            'model_expected_dims': None,
            'tokenizer_output_dims': None,
            'attention_mask_dims': None,
            'dimension_mismatches': []
        }
        
        if self.model and self.tokenizer:
            try:
                # Get expected dimensions from model
                model_dims = {}
                if hasattr(self.model, 'config'):
                    config = self.model.config
                    model_dims = {
                        'vocab_size': getattr(config, 'vocab_size', None),
                        'max_seq_len': getattr(config, 'max_seq_len', None),
                        'hidden_size': getattr(config, 'hidden_size', None)
                    }
                elif hasattr(self.model, 'tts') and hasattr(self.model.tts, 'config'):
                    config = self.model.tts.config
                    model_dims = {
                        'vocab_size': getattr(config, 'vocab_size', None),
                        'max_seq_len': getattr(config, 'max_seq_len', None),
                        'hidden_size': getattr(config, 'hidden_size', None)
                    }
                
                dimension_info['model_expected_dims'] = model_dims
                
                # Test with problematic text
                test_text = "ok.. well im feeling incredibly turned on by this direction"
                try:
                    if hasattr(self.tokenizer, 'encode'):
                        tokens = self.tokenizer.encode(test_text)
                    elif hasattr(self.tokenizer, '__call__'):
                        result = self.tokenizer(test_text)
                        tokens = result.get('input_ids', []) if isinstance(result, dict) else result
                    else:
                        tokens = []
                    
                    dimension_info['tokenizer_output_dims'] = {
                        'sequence_length': len(tokens),
                        'max_token_id': max(tokens) if tokens else None,
                        'vocab_coverage': len(set(tokens)) if tokens else None
                    }
                    
                    # Check for dimension mismatches
                    model_vocab = model_dims.get('vocab_size')
                    tokenizer_max = max(tokens) if tokens else None
                    
                    if model_vocab and tokenizer_max and tokenizer_max >= model_vocab:
                        dimension_info['dimension_mismatches'].append({
                            'type': 'vocab_size_mismatch',
                            'details': f"Tokenizer produces token {tokenizer_max} but model vocab is {model_vocab}",
                            'severity': 'critical',
                            'fix': 'Use matching tokenizer and model, or update model vocab size'
                        })
                
                except Exception as token_error:
                    dimension_info['tokenization_error'] = str(token_error)
                
            except Exception as e:
                self.issues_found.append({
                    'severity': 'high',
                    'category': 'dimension_matching',
                    'message': f"Dimension analysis failed: {str(e)}",
                    'traceback': traceback.format_exc()
                })
        
        return dimension_info
    
    def _calculate_severity_score(self) -> int:
        """Calculate overall severity score (0-100)."""
        if not self.issues_found:
            return 0
        
        severity_weights = {'low': 1, 'medium': 3, 'high': 7, 'critical': 15}
        total_score = sum(severity_weights.get(issue['severity'], 5) for issue in self.issues_found)
        return min(total_score, 100)
    
    def _generate_final_recommendations(self, report: Dict[str, Any]):
        """Generate final recommendations based on diagnostic results."""
        
        # Critical issues first
        critical_issues = [issue for issue in self.issues_found if issue['severity'] == 'critical']
        if critical_issues:
            self.recommendations.append({
                'priority': 'immediate',
                'action': 'Fix critical configuration mismatches',
                'details': 'You have critical issues that will cause crashes. Address these first.',
                'specific_fixes': [issue.get('fix', 'Check error details') for issue in critical_issues]
            })
        
        # Model/tokenizer compatibility
        model_info = report['model_info']
        tokenizer_info = report['tokenizer_info']
        
        if model_info.get('vocab_size') and tokenizer_info.get('vocab_size'):
            if model_info['vocab_size'] != tokenizer_info['vocab_size']:
                self.recommendations.append({
                    'priority': 'high',
                    'action': 'Fix vocab size mismatch',
                    'details': f"Model expects {model_info['vocab_size']} tokens but tokenizer has {tokenizer_info['vocab_size']}",
                    'specific_fixes': ['Use matching model and tokenizer versions', 'Check XTTS model configuration']
                })
        
        # Tensor operation issues
        tensor_info = report['tensor_compatibility']
        if tensor_info.get('tensor_creation_test'):
            failed_tests = [k for k, v in tensor_info['tensor_creation_test'].items() 
                          if isinstance(v, bool) and not v]
            if failed_tests:
                self.recommendations.append({
                    'priority': 'high',
                    'action': 'Fix tensor operation failures',
                    'details': f"Failed tests: {failed_tests}",
                    'specific_fixes': ['Check CUDA installation', 'Verify PyTorch version compatibility']
                })
        
        # If no major issues found
        if report['severity_score'] < 10:
            self.recommendations.append({
                'priority': 'low',
                'action': 'Configuration appears mostly correct',
                'details': 'The srcIndex error might be caused by a specific text input or edge case',
                'specific_fixes': ['Add input validation', 'Use the tensor validator from earlier']
            })
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted diagnostic report."""
        print("\n" + "="*60)
        print("XTTS CONFIGURATION DIAGNOSTIC REPORT")
        print("="*60)
        
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"Environment: {report['environment']}")
        print(f"Severity Score: {report['severity_score']}/100")
        
        if report['issues_found']:
            print(f"\nISSUES FOUND ({len(report['issues_found'])}):")
            for i, issue in enumerate(report['issues_found'], 1):
                print(f"\n{i}. [{issue['severity'].upper()}] {issue['category']}")
                print(f"   Message: {issue['message']}")
                if 'fix' in issue:
                    print(f"   Fix: {issue['fix']}")
        
        if report['recommendations']:
            print(f"\nRECOMMENDATIONS ({len(report['recommendations'])}):")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"\n{i}. [{rec['priority'].upper()}] {rec['action']}")
                print(f"   Details: {rec['details']}")
                if 'specific_fixes' in rec:
                    for fix in rec['specific_fixes']:
                        print(f"   - {fix}")
        
        print("\n" + "="*60)

# Convenience function
def diagnose_xtts_config(model=None, config=None, tokenizer=None, print_report=True):
    """
    Quick diagnostic function.
    
    Args:
        model: Your XTTS model
        config: Model configuration
        tokenizer: Tokenizer instance
        print_report: Whether to print the report
    
    Returns:
        Diagnostic report dictionary
    """
    diagnostic = XTTSDiagnostic(model, config, tokenizer)
    report = diagnostic.run_full_diagnostic()
    
    if print_report:
        diagnostic.print_report(report)
    
    return report

# Example usage
if __name__ == "__main__":
    print("XTTS Diagnostic Tool")
    print("Usage: diagnose_xtts_config(your_model, your_config, your_tokenizer)")
    print("This will identify why you're getting the srcIndex < srcSelectDimSize error.")