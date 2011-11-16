(provide erc-notify-over-ssh)

(defun visible-buffer-list ()
  "Returns a list of all buffers visible."
  (mapcar 'window-buffer
          (apply 'append
                 (mapcar 'window-list
                         (filter (lambda (x)
                                   (string-equal "F1" (frame-parameter x 'name)))
                                 (frame-list))))))

(defvar queued-notifications nil)
(defvar ssh-notify-process nil)

(defun send-queued-notifications (&optional port)
  (interactive)
  (unless port
    (setq port 4222))
  (when queued-notifications
    (dolist (n queued-notifications)
      (when (condition-case nil (setq ssh-notify-process (open-network-stream "ssh-notify-process" nil "localhost" port)) (error nil))
        (process-send-string ssh-notify-process (concat (nth 2 n) "|" (when (nth 1 n) (concat (nth 1 n) "|")) (nth 0 n)))
        (delete-process ssh-notify-process)))
    (setq queued-notifications nil)))

(defun notify-over-ssh-tunnel (message &optional summary args port)
  (interactive)
  (unless port
    (setq port 4222))
  (if (condition-case nil (setq ssh-notify-process (open-network-stream "ssh-notify-process" nil "localhost" port)) (error nil))
      (progn
        (delete-process ssh-notify-process)
        (send-queued-notifications port)
        (condition-case nil (setq ssh-notify-process (open-network-stream "ssh-notify-process" nil "localhost" port)) (error nil))
        (process-send-string ssh-notify-process (concat args "|" (when summary (concat summary "|")) message))
        (delete-process ssh-notify-process))
    (setq queued-notifications (append queued-notifications `((,message ,summary ,args))))))

(defun erc-notify-if-current-nick-mentioned (matched-type nick msg)
  (interactive)
  (when (eq matched-type 'current-nick)
    (notify-over-ssh-tunnel msg (car (split-string nick "!")) "-i call-start")))

(defun erc-notify-me-of-private-message (proc parsed)
  (let ((nick (car (erc-parse-user (erc-response.sender parsed))))
        (target (car (erc-response.command-args parsed)))
        (msg (erc-response.contents parsed)))
    (when (and (erc-current-nick-p target)
               (not (erc-is-message-ctcp-and-not-action-p msg)))
      (unless (any (lambda (b) (string-equal nick (buffer-name b))) (visible-buffer-list))
        (notify-over-ssh-tunnel msg nick))
      nil)))

(eval-after-load "erc-notify-over-ssh"
  '(progn
    (add-hook 'erc-text-matched-hook 'erc-notify-if-current-nick-mentioned)
    (add-hook 'erc-server-PRIVMSG-functions 'erc-notify-me-of-private-message))
