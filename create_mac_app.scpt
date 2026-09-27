-- ==============================================================================
-- AppleScript pour créer l'application macOS FinCoach.app (Terminal visible)
-- ==============================================================================

on run
    -- Récupérer le chemin dynamique du dossier parent dans lequel se trouve l'application .app
    set appPath to POSIX path of (path to me)
    set parentDir to do shell script "dirname " & quoted form of appPath
    
    -- Demander à Terminal de s'activer et de lancer le script dans une fenêtre visible
    tell application "Terminal"
        activate
        do script "cd " & quoted form of parentDir & " && ./run_fincoach.sh"
    end tell
end run
