$User = "User01"
$PWord = ConvertTo-SecureString -String "P@sSwOrd" -AsPlainText -Force
$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord
Send-MailMessage -From 'User01 <user01@neptune.com>' -To 'User02 <user02@neptune.com>' -Subject 'Test mail' -Body "Test body" -SmtpServer "mail.neptune.com" -Credential $Credential