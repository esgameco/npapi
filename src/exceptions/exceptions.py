"""
   __                    _   _                 
  /__\_  _____ ___ _ __ | |_(_) ___  _ __  ___ 
 /_\ \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|
//__  >  < (_|  __/ |_) | |_| | (_) | | | \__ \
\__/ /_/\_\___\___| .__/ \__|_|\___/|_| |_|___/
                  |_|                          
"""

class RegisterError(Exception):
    pass

class LoginError(Exception):
    pass

class PetCreationError(Exception):
    pass

class ActivationError(Exception):
    pass