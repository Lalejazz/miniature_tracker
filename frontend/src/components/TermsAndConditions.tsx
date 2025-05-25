/**
 * Terms and Conditions component
 */

import React from 'react';

interface TermsAndConditionsProps {
  isModal?: boolean;
  onAccept?: () => void;
  onDecline?: () => void;
  showButtons?: boolean;
}

export const TermsAndConditions: React.FC<TermsAndConditionsProps> = ({
  isModal = false,
  onAccept,
  onDecline,
  showButtons = false,
}) => {
  const containerClass = isModal ? 'terms-modal-content' : 'terms-standalone';

  return (
    <div className={containerClass}>
      <h2>Terms and Conditions</h2>
      <div className="terms-content">
        <section>
          <h3>1. Acceptance of Terms</h3>
          <p>
            By creating an account and using Miniature Tracker, you agree to be bound by these Terms and Conditions. 
            If you do not agree to these terms, please do not use our service.
          </p>
        </section>

        <section>
          <h3>2. Description of Service</h3>
          <p>
            Miniature Tracker is a web application that allows users to track their miniature wargaming collections, 
            painting progress, and connect with other players in their area. The service includes features for:
          </p>
          <ul>
            <li>Managing miniature collections and painting status</li>
            <li>Tracking painting progress and statistics</li>
            <li>Discovering and connecting with other players</li>
            <li>Importing and exporting collection data</li>
          </ul>
        </section>

        <section>
          <h3>3. User Accounts and Registration</h3>
          <p>
            To use certain features of our service, you must create an account. You agree to:
          </p>
          <ul>
            <li>Provide accurate and complete information during registration</li>
            <li>Maintain the security of your account credentials</li>
            <li>Verify your email address to activate your account</li>
            <li>Notify us immediately of any unauthorized use of your account</li>
          </ul>
        </section>

        <section>
          <h3>4. Privacy and Data Protection</h3>
          <p>
            We are committed to protecting your privacy. Our data practices include:
          </p>
          <ul>
            <li>We collect only the information necessary to provide our services</li>
            <li>Your email address is used for account verification and service communications</li>
            <li>Location data is used only for player discovery features and is not shared without consent</li>
            <li>You can control the visibility of your contact information in player discovery</li>
            <li>We do not sell or share your personal data with third parties for marketing purposes</li>
          </ul>
        </section>

        <section>
          <h3>5. User Content and Conduct</h3>
          <p>
            You are responsible for all content you submit to our service. You agree to:
          </p>
          <ul>
            <li>Not upload content that is illegal, harmful, or violates others' rights</li>
            <li>Respect other users and maintain a friendly community environment</li>
            <li>Not use the service for spam, harassment, or malicious activities</li>
            <li>Ensure accuracy of your collection data and player information</li>
          </ul>
        </section>

        <section>
          <h3>6. Intellectual Property</h3>
          <p>
            Game system names, faction names, and related intellectual property belong to their respective owners 
            (Games Workshop, Privateer Press, etc.). Miniature Tracker is an independent fan project and is not 
            affiliated with or endorsed by any game manufacturer.
          </p>
        </section>

        <section>
          <h3>7. Service Availability</h3>
          <p>
            We strive to maintain service availability but cannot guarantee uninterrupted access. We reserve the 
            right to modify, suspend, or discontinue the service with reasonable notice.
          </p>
        </section>

        <section>
          <h3>8. Data Export and Account Deletion</h3>
          <p>
            You have the right to:
          </p>
          <ul>
            <li>Export your collection data at any time in JSON or CSV format</li>
            <li>Request deletion of your account and associated data</li>
            <li>Update or correct your personal information</li>
          </ul>
        </section>

        <section>
          <h3>9. Limitation of Liability</h3>
          <p>
            Miniature Tracker is provided "as is" without warranties. We are not liable for any damages arising 
            from use of the service, including but not limited to data loss or service interruptions.
          </p>
        </section>

        <section>
          <h3>10. Changes to Terms</h3>
          <p>
            We may update these terms from time to time. Continued use of the service after changes constitutes 
            acceptance of the new terms. We will notify users of significant changes via email or service announcements.
          </p>
        </section>

        <section>
          <h3>11. Contact Information</h3>
          <p>
            If you have questions about these Terms and Conditions, please contact us through the application 
            or via the contact information provided in our documentation.
          </p>
        </section>

        <section>
          <h3>12. Governing Law</h3>
          <p>
            These terms are governed by applicable local laws. Any disputes will be resolved through appropriate 
            legal channels in the jurisdiction where the service is operated.
          </p>
        </section>
      </div>

      {showButtons && (
        <div className="terms-actions">
          <button 
            type="button" 
            className="btn-secondary" 
            onClick={onDecline}
          >
            Decline
          </button>
          <button 
            type="button" 
            className="btn-primary" 
            onClick={onAccept}
          >
            Accept Terms
          </button>
        </div>
      )}
    </div>
  );
}; 