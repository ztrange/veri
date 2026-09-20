Describe 'shellspec runs at all'
  It 'passes'
    When call echo hi
    The output should equal 'hi'
    The status should be success
  End
End
