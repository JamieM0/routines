import json
import os
import sys
from pathlib import Path

def read_json_file(file_path):
    """Read a JSON file and return its contents as a Python dictionary."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_automation_timeline_html(timeline_data):
    """Generate HTML for the automation timeline section."""
    html = '<div class="automation-timeline">\n'
    html += '    <h3>Automation Development Timeline</h3>\n'

    # Historical timeline entries
    for year, content in timeline_data['timeline']['historical'].items():
        html += f'    <div class="timeline-entry">\n'
        html += f'        <div class="timeline-year">{year}</div>\n'
        html += f'        <div class="timeline-content">\n'
        # Check for and process bold text (** pattern)
        content = process_bold_text(content)
        html += f'            <p>{content}</p>\n'
        html += f'        </div>\n'
        html += f'    </div>\n'

    # Predictions timeline entries - with teal color for year background and italics for content
    for year, content in timeline_data['timeline']['predictions'].items():
        html += f'    <div class="timeline-entry">\n'
        html += f'        <div class="timeline-year-prediction">{year}</div>\n'
        html += f'        <div class="timeline-content">\n'
        # Check for and process bold text (** pattern)
        content = process_bold_text(content)
        # Add italics to the prediction text
        html += f'            <p><em>{content}</em></p>\n'
        html += f'        </div>\n'
        html += f'    </div>\n'

    html += '</div>\n'
    return html

def process_bold_text(text):
    """Replace text surrounded by ** with HTML bold tags."""
    import re
    # Find all text surrounded by ** and replace with <strong> tags
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

def generate_automation_challenges_html(challenges_data):
    """Generate HTML for the automation challenges section."""
    html = '<div class="automation-challenges">\n'
    html += f'    <h3>Current Automation Challenges</h3>\n'
    if "topic" in challenges_data["challenges"]:
        html += f'    <p>Despite significant progress, several challenges remain in fully automating the {challenges_data["challenges"]["topic"].split()[0].lower()} process:</p>\n'
    elif "field" in challenges_data["challenges"]:
        html += f'    <p>Despite significant progress, several challenges remain in fully automating the {challenges_data["challenges"]["field"].split()[0].lower()} process:</p>\n'
    else:
        html += '    <p>Despite significant progress, several challenges remain in fully automating the process:</p>\n'
    html += f'    <ul>\n'

    for challenge in challenges_data['challenges']['challenges']:
        # Split explanation into paragraphs if needed
        explanations = challenge['explanation'].split('  ')
        html += f'        <li><strong>{challenge["title"]}:</strong> {explanations[0]}</li>\n'

    html += f'    </ul>\n'
    html += '</div>\n'
    return html

def generate_standard_process_html(tree_data):
    """Generate HTML for the standard process tab content."""
    html = '<div id="standard-process" class="tab-content active">\n'

    # Process each top-level step in the tree
    for i, step in enumerate(tree_data['tree']['children']):
        html += f'    <div class="process-section">\n'
        html += f'        <h3>{i+1}. {step["step"]}</h3>\n'
        # Add a placeholder description
        html += f'        <p>This step involves {step["step"].lower()}.</p>\n'
        html += f'        <h4>Key Steps:</h4>\n'
        html += f'        <ul class="step-list">\n'

        # Add child steps if they exist
        if "children" in step:
            for child_step in step["children"]:
                html += f'            <li>{child_step["step"]}</li>\n'

        html += f'        </ul>\n'
        # Add a placeholder automation status
        html += f'        <p><strong>Automation Status:</strong> Currently being developed and refined.</p>\n'
        html += f'    </div>\n'

    # Add timeline and challenges sections
    html += '    {{TIMELINE_PLACEHOLDER}}\n'
    html += '    {{CHALLENGES_PLACEHOLDER}}\n'
    html += '</div>\n'
    return html


def generate_automation_pathway_html(adoption_data, implementation_data, roi_data):
    """Generate HTML for the automation pathway tab content."""
    html = '<div id="automation-pathway" class="tab-content">\n'

    # Automation Adoption Framework section
    html += '    <div class="process-section">\n'
    html += '        <h3>Automation Adoption Framework</h3>\n'
    html += '        <p>This framework outlines the pathway to full automation, detailing the progression from manual processes to fully automated systems.</p>\n'

    # Process each phase in the adoption data
    phase_keys = sorted([k for k in adoption_data.keys() if k.startswith('phase')])
    for phase_key in phase_keys:
        phase = adoption_data[phase_key]
        # Process bold text in the title
        title = process_bold_text(phase["title"])
        status = process_bold_text(phase["status"])
        html += f'        <h4>{title} ({status})</h4>\n'
        html += '        <ul class="step-list">\n'
        for example in phase["examples"]:
            # Process bold text in each example
            example = process_bold_text(example)
            html += f'            <li>{example}</li>\n'
        html += '        </ul>\n'

    html += '    </div>\n'

    # Current Implementation Levels section
    html += '    <div class="process-section">\n'
    html += '        <h3>Current Implementation Levels</h3>\n'
    html += '        <p>The table below shows the current automation levels across different scales:</p>\n'
    html += '        <table class="automation-table">\n'
    html += '            <thead>\n'
    html += '                <tr>\n'
    html += '                    <th>Process Step</th>\n'
    html += '                    <th>Small Scale</th>\n'
    html += '                    <th>Medium Scale</th>\n'
    html += '                    <th>Large Scale</th>\n'
    html += '                </tr>\n'
    html += '            </thead>\n'
    html += '            <tbody>\n'

    # Correctly access the implementation data
    for step in implementation_data["implementation_assessment"]["process_steps"]:
        # Process bold text in each cell
        step_name = process_bold_text(step["step_name"])
        low_scale = process_bold_text(step["automation_levels"]["low_scale"])
        medium_scale = process_bold_text(step["automation_levels"]["medium_scale"])
        high_scale = process_bold_text(step["automation_levels"]["high_scale"])
        
        html += '                <tr>\n'
        html += f'                    <td>{step_name}</td>\n'
        html += f'                    <td>{low_scale}</td>\n'
        html += f'                    <td>{medium_scale}</td>\n'
        html += f'                    <td>{high_scale}</td>\n'
        html += '                </tr>\n'

    html += '            </tbody>\n'
    html += '        </table>\n'
    html += '    </div>\n'

    # ROI Analysis section - FIXED to match the actual JSON structure
    html += '    <div class="process-section">\n'
    html += '        <h3>Automation ROI Analysis</h3>\n'
    html += '        <p>The return on investment for automation depends on scale and production volume:</p>\n'
    html += '        <ul class="step-list">\n'

    # Correctly access the nested ROI timeframe data
    for scale in ["small_scale", "medium_scale", "large_scale"]:
        if "roi_analysis" in roi_data and scale in roi_data["roi_analysis"]:
            # Make sure timeframe exists and handle different possible structures
            scale_data = roi_data["roi_analysis"][scale]
            if isinstance(scale_data, dict) and "timeframe" in scale_data:
                timeframe = process_bold_text(scale_data["timeframe"])
                scale_display = scale.replace('_', ' ').title()
                html += f'            <li><strong>{scale_display}:</strong> {timeframe}</li>\n'

    html += '        </ul>\n'

    # Key benefits section
    if "key_benefits" in roi_data:
        # Check if key_benefits is a list or a string
        if isinstance(roi_data["key_benefits"], list):
            if len(roi_data["key_benefits"]) > 0:
                # Handle case where key_benefits is a list
                # Process bold text in each benefit
                processed_benefits = [process_bold_text(benefit) for benefit in roi_data["key_benefits"]]
                
                html += '        <p>Key benefits driving ROI include '
                if len(processed_benefits) == 1:
                    html += f'{processed_benefits[0]}.</p>\n'
                else:
                    html += ', '.join(processed_benefits[:-1]) + ', and ' + \
                            processed_benefits[-1] + '.</p>\n'
        elif isinstance(roi_data["key_benefits"], str):
            # Handle case where key_benefits is a string
            processed_benefit = process_bold_text(roi_data["key_benefits"])
            html += f'        <p>Key benefits driving ROI include {processed_benefit}.</p>\n'

    html += '    </div>\n'
    html += '</div>\n'
    return html

def generate_technical_details_html(future_tech_data, specs_data):
    """Generate HTML for the technical details tab content."""
    html = '<div id="technical-details" class="tab-content">\n'

    # Automation Technologies section
    html += '    <div class="process-section">\n'
    html += '        <h3>Automation Technologies</h3>\n'
    html += '        <p>This section details the underlying technologies enabling automation.</p>\n'

    # Sensory Systems
    html += '        <h4>Sensory Systems</h4>\n'
    html += '        <ul class="step-list">\n'
    for sensor in future_tech_data["sensory_systems"]:
        name = process_bold_text(sensor["name"])
        description = process_bold_text(sensor["description"])
        html += f'            <li><strong>{name}:</strong> {description}</li>\n'
    html += '        </ul>\n'

    # Control Systems
    html += '        <h4>Control Systems</h4>\n'
    html += '        <ul class="step-list">\n'
    for control in future_tech_data["control_systems"]:
        name = process_bold_text(control["name"])
        description = process_bold_text(control["description"])
        html += f'            <li><strong>{name}:</strong> {description}</li>\n'
    html += '        </ul>\n'

    # Mechanical Systems
    html += '        <h4>Mechanical Systems</h4>\n'
    html += '        <ul class="step-list">\n'
    for mech in future_tech_data["mechanical_systems"]:
        name = process_bold_text(mech["name"])
        description = process_bold_text(mech["description"])
        html += f'            <li><strong>{name}:</strong> {description}</li>\n'
    html += '        </ul>\n'

    # Software Integration
    html += '        <h4>Software Integration</h4>\n'
    html += '        <ul class="step-list">\n'
    for software in future_tech_data["software_integration"]:
        name = process_bold_text(software["name"])
        description = process_bold_text(software["description"])
        html += f'            <li><strong>{name}:</strong> {description}</li>\n'
    html += '        </ul>\n'
    html += '    </div>\n'

    # Technical Specifications section
    html += '    <div class="process-section">\n'
    html += '        <h3>Technical Specifications for Commercial Automation</h3>\n'
    html += '        <p>Standard parameters for industrial production:</p>\n'

    # Performance Metrics
    html += '        <h4>Performance Metrics</h4>\n'
    html += '        <ul class="step-list">\n'
    for metric in specs_data["performance_metrics"]:
        # Process name and value with bold text function
        name = process_bold_text(metric["name"])
        value = process_bold_text(metric["value"])
        
        # Handle various possible structures for the range information
        range_info = ""
        if "range" in metric:
            range_text = process_bold_text(metric['range'])
            range_info = f" (Range: {range_text})"
        elif "description" in metric:
            # If no range field but description exists, include the description instead
            desc_text = process_bold_text(metric['description'])
            range_info = f" - {desc_text}"
            
        html += f'            <li>{name}: {value}{range_info}</li>\n'
    html += '        </ul>\n'

    # Implementation Requirements
    html += '        <h4>Implementation Requirements</h4>\n'
    html += '        <ul class="step-list">\n'
    for req in specs_data["implementation_requirements"]:
        # Process name with bold text function
        name = process_bold_text(req["name"])
        
        # Handle different field names for specification
        spec_info = ""
        if "specification" in req:
            spec_info = process_bold_text(req["specification"])
        elif "value" in req:
            spec_info = process_bold_text(req["value"])
        elif "description" in req:
            spec_info = process_bold_text(req["description"])
        else:
            spec_info = "Specification not available"
            
        html += f'            <li>{name}: {spec_info}</li>\n'
    html += '        </ul>\n'
    html += '    </div>\n'

    html += '</div>\n'
    return html

def generate_tree_preview_text(tree_data):
    """Generate a text representation of a tree suitable for the approach preview."""
    # Use the first level (root) and second level (main steps) of the tree for the preview
    root_name = tree_data.get("tree", {}).get("step", "approach_root").lower().replace(" ", "_")
    
    # Start with the root node
    lines = [root_name]
    
    # Add child nodes with ASCII art tree structure
    children = tree_data.get("tree", {}).get("children", [])
    for i, child in enumerate(children):
        # Get a shortened UUID to use in the preview
        uuid_part = child.get("uuid", "")[:4] if "uuid" in child else str(i)
        
        child_step = child.get("step", "step").lower().replace(" ", "_")
        # Make the child step name and uuid shorter for the preview
        child_name = f"{child_step}_{uuid_part}"
        
        # Last child has a different prefix
        if i == len(children) - 1:
            lines.append(f"└── {child_name}")
        else:
            lines.append(f"├── {child_name}")
        
        # Add grandchildren for this child with proper indentation
        grandchildren = child.get("children", [])
        for j, grandchild in enumerate(grandchildren):
            # Get a shortened UUID for the grandchild
            g_uuid_part = grandchild.get("uuid", "")[:4] if "uuid" in grandchild else str(j)
            
            g_step = grandchild.get("step", "substep").lower().replace(" ", "_")
            # Make the grandchild step name and uuid shorter for the preview
            g_name = f"{g_step}_{g_uuid_part}"
            
            # Use different prefixes based on whether this is the last child and last grandchild
            if i == len(children) - 1:  # Last child
                if j == len(grandchildren) - 1:  # Last grandchild
                    lines.append(f"    └── {g_name}")
                else:
                    lines.append(f"    ├── {g_name}")
            else:  # Not last child
                if j == len(grandchildren) - 1:  # Last grandchild
                    lines.append(f"│   └── {g_name}")
                else:
                    lines.append(f"│   ├── {g_name}")
                    
            # Limit the preview to a reasonable size
            if j >= 2 and len(grandchildren) > 4:
                lines.append(f"│   └── ... ({len(grandchildren) - 3} more steps)")
                break
        
        # Limit the preview to a reasonable number of main steps
        if i >= 2 and len(children) > 4:
            lines.append(f"└── ... ({len(children) - 3} more steps)")
            break
    
    return "\n".join(lines)

def generate_competing_approaches_html(alt_trees_data=None):
    """Generate HTML for the competing approaches tab content."""
    html = '<div id="competing-approaches" class="tab-content">\n'
    html += '    <div class="process-section">\n'
    html += '        <h3>Alternative Approaches</h3>\n'
    html += '        <p>These are alternative automation trees generated by different versions of our Iterative AI algorithm. Browse these competing models and vote for approaches you find most effective.</p>\n'
    html += '    </div>\n'

    # Approaches grid
    html += '    <div class="approaches-grid">\n'

    # If we have real alternative trees, use them
    if alt_trees_data and len(alt_trees_data) > 0:
        for i, alt_tree in enumerate(alt_trees_data):
            approach_name = alt_tree.get("approach_name", f"Alternative Approach {i+1}")
            approach_desc = alt_tree.get("approach_description", "An alternative methodology for approaching this process.")
            
            # Generate a preview of the tree structure
            tree_preview = generate_tree_preview_text(alt_tree)
            
            # Random-ish vote counts that decrease as index increases
            vote_count = max(5, 42 - (i * 8) + (i * i))
            
            html += f'        <div class="approach-card">\n'
            html += f'            <h4>{approach_name}</h4>\n'
            html += f'            <p>{approach_desc}</p>\n'
            html += f'            <div class="approach-preview">\n{tree_preview}</div>\n'
            html += '            <div class="approach-meta">\n'
            html += f'                <p>Created by: Iterative AI Alpha</p>\n'
            html += f'                <p>Votes: <span class="vote-count">{vote_count}</span></p>\n'
            html += '            </div>\n'
            html += '            <div class="approach-actions">\n'
            html += '                <button class="button secondary vote-button">\n'
            html += '                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\n'
            html += '                        <path d="M12 4L18 10H6L12 4Z" fill="currentColor"/>\n'
            html += '                    </svg>\n'
            html += '                    Vote Up\n'
            html += '                </button>\n'
            html += '                <a href="#" class="button secondary">View Full Tree</a>\n'
            html += '            </div>\n'
            html += '        </div>\n'
    else:
        # Default placeholders if no alternatives
        html += '        <div class="approach-card">\n'
        html += '            <h4>Efficiency-Optimized Approach</h4>\n'
        html += '            <p>This approach prioritizes minimizing resource usage and production time.</p>\n'
        html += '            <div class="approach-preview">\n'
        html += 'efficiency_optimized\n'
        html += '├── sensor_data_collection_8f29\n'
        html += '│   ├── lidar_scanning_a421\n'
        html += '│   └── camera_imaging_c731\n'
        html += '├── data_processing_d54f\n'
        html += '│   ├── object_detection_b651\n'
        html += '│   ├── path_planning_e922\n'
        html += '│   └── decision_making_f110\n'
        html += '├── control_execution_4a12\n'
        html += '└── monitoring_feedback_7b29</div>\n'
        html += '            <div class="approach-meta">\n'
        html += '                <p>Created by: Iterative AI v2.3</p>\n'
        html += '                <p>Votes: <span class="vote-count">18</span></p>\n'
        html += '            </div>\n'
        html += '            <div class="approach-actions">\n'
        html += '                <button class="button secondary vote-button">\n'
        html += '                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\n'
        html += '                        <path d="M12 4L18 10H6L12 4Z" fill="currentColor"/>\n'
        html += '                    </svg>\n'
        html += '                    Vote Up\n'
        html += '                </button>\n'
        html += '                <a href="#" class="button secondary">View Full Tree</a>\n'
        html += '            </div>\n'
        html += '        </div>\n'

    html += '    </div>\n'

    # Why Multiple Approaches section
    html += '    <div class="process-section">\n'
    html += '        <h3>Why Multiple Approaches?</h3>\n'
    html += '        <p>Different methodologies offer unique advantages depending on context:</p>\n'
    html += '        <ul class="step-list">\n'
    html += '            <li><strong>Scale considerations:</strong> Some approaches work better for large-scale production, while others are more suitable for specialized applications</li>\n'
    html += '            <li><strong>Resource constraints:</strong> Different methods optimize for different resources (time, computing power, energy)</li>\n'
    html += '            <li><strong>Quality objectives:</strong> Approaches vary in their emphasis on safety, efficiency, adaptability, and reliability</li>\n'
    html += '            <li><strong>Automation potential:</strong> Some approaches are more easily adapted to full automation than others</li>\n'
    html += '        </ul>\n'
    html += '        <p>By voting for approaches you find most effective, you help our community identify the most promising automation pathways.</p>\n'
    html += '    </div>\n'
    html += '</div>\n'

    return html

def generate_breadcrumbs_html(breadcrumbs):
    """Generate HTML for customized breadcrumbs navigation."""
    if not breadcrumbs:
        return None
        
    # Split the breadcrumbs by '/'
    parts = breadcrumbs.split('/')
    
    # Generate HTML for breadcrumbs
    html = '<div class="breadcrumbs">\n'
    html += '    <span><a href="/index">Home</a></span>\n'
    
    # Build the path incrementally for each part
    path = ""
    for i, part in enumerate(parts[:-1]):  # All but the last part (current page)
        path += f"/{part}"
        display_name = part.replace('-', ' ').title()
        html += f'    <span><a href="{path}/index">{display_name}</a></span>\n'
    
    # Add the current page (last part) without a link
    current_page = parts[-1].replace('-', ' ').title()
    html += f'    <span>{current_page}</span>\n'
    html += '</div>\n'
    
    return html

def generate_page_html(template_html, metadata, tree_data, timeline_data, challenges_data,
                       adoption_data, implementation_data, roi_data, future_tech_data, specs_data, breadcrumbs, alt_trees_data=None):
    """Generate the complete HTML page using the template and JSON data."""
    # Replace title, subtitle, and status
    new_html = template_html.replace('Bread Making', metadata['page_metadata']['title'])
    new_html = new_html.replace('<span>Bread Making</span>', f'<span>{metadata["page_metadata"]["title"]}</span>')
    new_html = new_html.replace('<span>Partial Automation Available</span>', f'<span>{metadata["page_metadata"]["automation_status"]}</span>')

    # Replace the subtitle (fixing the bread production issue)
    new_html = new_html.replace(
        '<p class="hero-subtitle">Exploring automation possibilities in artisanal and commercial bread production</p>',
        f'<p class="hero-subtitle">{metadata["page_metadata"]["subtitle"]}</p>'
    )

    # Replace progress bar (assuming 50% for partial automation, adjust as needed)
    # Check if progress is in automation_progress or progress_percentage field
    if 'automation_progress' in metadata['page_metadata']:
        progress_text = metadata['page_metadata']['automation_progress']
    elif 'progress_percentage' in metadata['page_metadata']:
        progress_text = metadata['page_metadata']['progress_percentage']
    else:
        progress_text = "50%"  # Default fallback
        
    # Remove any non-digit characters and convert to integer
    progress_percentage = int(''.join(filter(str.isdigit, progress_text)))
    progress_style = f'style="width: {progress_percentage}%;"'
    new_html = new_html.replace('<div class="progress-fill"></div>', f'<div class="progress-fill" {progress_style}></div>')

    # Replace article summary
    summary_paragraphs = metadata['page_metadata']['explanatory_text'].split('\n\n')
    summary_html = ""
    for paragraph in summary_paragraphs:
        summary_html += f'<p>{paragraph}</p>\n'

    new_html = new_html.replace('<div class="article-summary">\n                        <p>Bread making is a multistep process that combines science and artistry. From gathering ingredients to the final rise and baking, each step presents unique automation opportunities. At present, commercial bakeries have achieved partial automation, with certain processes still benefiting from human expertise and intervention.</p>\n                        <p>This workflow breaks down the bread making process into manageable steps, illustrating both current automation capabilities and areas for future development.</p>\n                    </div>',
                      f'<div class="article-summary">\n{summary_html}</div>')

    # Generate tab content
    standard_process_html = generate_standard_process_html(tree_data)
    automation_pathway_html = generate_automation_pathway_html(adoption_data, implementation_data, roi_data)
    technical_details_html = generate_technical_details_html(future_tech_data, specs_data)
    competing_approaches_html = generate_competing_approaches_html(alt_trees_data)

    # Generate timeline and challenges HTML
    timeline_html = generate_automation_timeline_html(timeline_data)
    challenges_html = generate_automation_challenges_html(challenges_data)

    # Replace placeholders in standard process tab
    standard_process_html = standard_process_html.replace("{{TIMELINE_PLACEHOLDER}}", timeline_html)
    standard_process_html = standard_process_html.replace("{{CHALLENGES_PLACEHOLDER}}", challenges_html)

    # Replace tab content in the template
    tab_content_start = new_html.find('<!-- Standard Process Tab Content -->')
    tab_content_end = new_html.find('<!-- Footer placeholder to be filled by components.js -->')

    tab_content = (
        '<!-- Standard Process Tab Content -->\n'
        f'{standard_process_html}\n'
        '<!-- Automation Pathway Tab Content -->\n'
        f'{automation_pathway_html}\n'
        '<!-- Technical Details Tab Content -->\n'
        f'{technical_details_html}\n'
        '<!-- Competing Approaches Tab Content -->\n'
        f'{competing_approaches_html}\n'
        '                    <div class="contributors-section">\n'
        '                        <h3>Contributors</h3>\n'
        f'                        <p>This workflow was developed using Iterative AI analysis of {metadata["page_metadata"]["title"].lower()} processes with input from professional engineers and automation experts.</p>\n'
        '                        <p><em>Last updated: April 2024</em></p>\n'
        '                        <a href="#" class="button secondary" id="suggest-improvements">Suggest Improvements</a>\n'
        '                        \n'
        '                        <!-- Feedback form container (initially hidden) -->\n'
        '                        <div id="feedback-form-container" class="feedback-form-container">\n'
        '                            <h4>Suggest Improvements</h4>\n'
        f'                            <p>We value your input on how to improve this {metadata["page_metadata"]["title"].lower()} workflow. Please provide your suggestions below.</p>\n'
        '                            \n'
        '                            <form id="feedback-form" class="feedback-form">\n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-name">Name (optional)</label>\n'
        '                                    <input type="text" id="feedback-name" name="name" placeholder="Your name">\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-email">Email (optional)</label>\n'
        '                                    <input type="email" id="feedback-email" name="email" placeholder="your@email.com">\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-subject">Subject</label>\n'
        '                                    <input type="text" id="feedback-subject" name="subject" placeholder="Brief description of your suggestion" required>\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-form-field">\n'
        '                                    <label for="feedback-body">Feedback Details</label>\n'
        '                                    <textarea id="feedback-body" name="message" placeholder="Please describe your suggestion in detail..." required></textarea>\n'
        '                                </div>\n'
        '                                \n'
        '                                <div class="feedback-actions">\n'
        '                                    <button type="button" id="cancel-feedback" class="button secondary">Cancel</button>\n'
        '                                    <button type="submit" id="send-feedback" class="button primary">Send Feedback</button>\n'
        '                                </div>\n'
        '                            </form>\n'
        '                            \n'
        '                            <div id="feedback-message" class="feedback-message"></div>\n'
        '                        </div>\n'
        '                    </div>\n'
    )

    new_html = new_html[:tab_content_start] + tab_content + new_html[tab_content_end:]

    # Update breadcrumb
    if breadcrumbs:
        breadcrumbs_html = generate_breadcrumbs_html(breadcrumbs)
        # Find and replace the entire default breadcrumbs section
        breadcrumbs_start = new_html.find('<div class="breadcrumbs">')
        if breadcrumbs_start != -1:
            breadcrumbs_end = new_html.find('</div>', breadcrumbs_start) + 6  # Include the closing </div>
            new_html = new_html[:breadcrumbs_start] + breadcrumbs_html + new_html[breadcrumbs_end:]
        else:
            # Fallback if the exact structure isn't found
            new_html = new_html.replace('<span><a href="/food-production/baking/index">Baking</a></span>', breadcrumbs_html)

    return new_html

def main():
    """Main function to generate HTML based on JSON files."""
    usage_msg = "Usage: python assemble.py <flow_dir> [output_path] [breadcrumbs]"
    
    if len(sys.argv) < 2:
        print(usage_msg)
        sys.exit(1)
        
    flow_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    breadcrumbs = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check if breadcrumbs file exists in the flow directory and use it if no breadcrumbs provided
    breadcrumbs_file = os.path.join(flow_dir, "breadcrumbs.txt")
    if not breadcrumbs and os.path.exists(breadcrumbs_file):
        with open(breadcrumbs_file, "r", encoding="utf-8") as f:
            breadcrumbs = f.read().strip()
    
    # Check if the flow directory exists
    if not os.path.isdir(flow_dir):
        print(f"Error: Flow directory '{flow_dir}' not found")
        sys.exit(1)
    
    # Define paths to JSON files in the flow directory
    metadata_path = os.path.join(flow_dir, "1.json")
    tree_path = os.path.join(flow_dir, "2.json")
    timeline_path = os.path.join(flow_dir, "3.json")
    challenges_path = os.path.join(flow_dir, "4.json")
    adoption_path = os.path.join(flow_dir, "5.json")
    implementation_path = os.path.join(flow_dir, "6.json")
    roi_path = os.path.join(flow_dir, "7.json")
    future_tech_path = os.path.join(flow_dir, "8.json")
    specs_path = os.path.join(flow_dir, "9.json")
    
    # Find alternative tree files if they exist
    alternative_trees = []
    i = 1
    while True:
        alt_path = os.path.join(flow_dir, f"alt{i}.json")
        if os.path.exists(alt_path):
            alternative_trees.append(alt_path)
            i += 1
        else:
            break
    
    print(f"Found {len(alternative_trees)} alternative tree files")
    
    # Path to the template HTML
    template_path = os.path.join("flow", "template.html")
    
    # If template doesn't exist in the specified location, try a relative path
    if not os.path.exists(template_path):
        template_path = "template.html"
        
        # If that doesn't exist either, check if it exists in the flow directory
        if not os.path.exists(template_path):
            template_path = os.path.join(flow_dir, "..", "template.html")
    
    # Read template HTML
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_html = f.read()
    except FileNotFoundError:
        print(f"Error: Template HTML file not found at '{template_path}'")
        sys.exit(1)
    
    try:
        # Read JSON data
        metadata = read_json_file(metadata_path)
        tree_data = read_json_file(tree_path)
        timeline_data = read_json_file(timeline_path)
        challenges_data = read_json_file(challenges_path)
        adoption_data = read_json_file(adoption_path)["automation_adoption"]
        implementation_data = read_json_file(implementation_path)
        roi_data = read_json_file(roi_path)
        
        # Ensure roi_data is properly structured for use
        if "roi_analysis" not in roi_data and "roi_analysis" in roi_data:
            # This is a no-op condition, left for clarity
            pass
        else:
            # Create a normalized structure
            roi_data = {"roi_analysis": roi_data}
        
        future_tech_data = read_json_file(future_tech_path)["future_technology"]
        specs_data = read_json_file(specs_path)["industrial_specifications"]
        
        # Process alternative trees
        alt_trees_data = []
        approach_names = ["Efficiency-Optimized Approach", "Safety-Optimized Approach", "Hybridized Approach"]
        approach_descs = [
            "This approach prioritizes minimizing resource usage and production time.",
            "This approach focuses on maximizing safety and reliability.",
            "This approach balances efficiency with safety considerations."
        ]
        
        for i, alt_path in enumerate(alternative_trees):
            try:
                alt_data = read_json_file(alt_path)
                # Add names and descriptions
                approach_name = approach_names[i] if i < len(approach_names) else f"Alternative Approach {i+1}"
                approach_desc = approach_descs[i] if i < len(approach_descs) else "An alternative methodology for approaching this process."
                alt_data["approach_name"] = approach_name
                alt_data["approach_description"] = approach_desc
                alt_trees_data.append(alt_data)
            except Exception as e:
                print(f"Warning: Error processing alternative tree {alt_path}: {e}")
                continue

        # Generate new HTML page
        new_html = generate_page_html(
            template_html,
            metadata,
            tree_data,
            timeline_data,
            challenges_data,
            adoption_data,
            implementation_data,
            roi_data,
            future_tech_data,
            specs_data,
            breadcrumbs,
            alt_trees_data
        )

        # Determine output path
        if output_path is None:
            # Save to the flow directory by default
            output_path = os.path.join(flow_dir, "output.html")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write the generated HTML to a file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_html)

        print(f"Generated HTML page: {os.path.abspath(output_path)}")
        
    except FileNotFoundError as e:
        print(f"Error: Missing required JSON file: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Invalid JSON structure: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating HTML: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()