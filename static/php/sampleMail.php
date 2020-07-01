<?php
	if($_SERVER['REQUEST_METHOD'] == "POST")
	{
		if(mail("youremail4@email.com", "New Sample User!", "User: " . $_POST["firstname"] . " Email: " . $_POST["email"], $headers))
                     echo "You've been successfully subscribed!";
                else
                     echo "There was a problem!";
	}
?>